import os
import pefile
from collections import defaultdict
from tqdm import tqdm
from functools import lru_cache
from concurrent.futures import as_completed

class Dependency:
    def __init__(self, name):
        self.name = name
        self.delay_loaded = False
        self.missing = False
        self.invalid = False
        self.is_system = False

    def __repr__(self):
        flags = [
            "❌" if self.missing else "",
            "❗" if self.invalid else "",
            "⏱" if self.delay_loaded else "",
            "[SYS]" if self.is_system else ""
        ]
        return f"{self.name} {' '.join(f for f in flags if f)}"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Dependency) and self.name == other.name

class DependencyGraph:
    def __init__(self):
        self.children = defaultdict(list)
        self.parents = defaultdict(list)
        self.nodes = set()

    def add_edge(self, parent, child):
        self.children[parent].append(child)
        self.parents[child].append(parent)
        self.nodes.update([parent, child])

    def print_tree(self, max_depth=8):
        def recurse(node, prefix="", is_last=True, depth=0, path=None):
            if path is None:
                path = set()
            connector = "└── " if is_last else "├── "
            label = str(node)
            if node in path and node not in self.parents.get(node, []):
                label += " 🔁"
            print(f"{prefix}{connector}{label}", flush=True)
            if node in path or (max_depth and depth >= max_depth):
                return
            path.add(node)
            children = self.children.get(node, [])
            for i, child in enumerate(children):
                recurse(child, prefix + ("    " if is_last else "│   "), i == len(children) - 1, depth + 1, path)
            path.remove(node)

        roots = [n for n in self.nodes if n not in self.parents]
        for i, root in enumerate(roots):
            recurse(root, "", i == len(roots) - 1)

    def export_dot(self):
        lines = ["digraph G {"]
        for parent, children in self.children.items():
            for child in children:
                lines.append(f'    "{parent.name}" -> "{child.name}";')
        lines.append("}")
        return "\n".join(lines)

def parse_file_for_dependencies(args):
    file_path, detect_system = args
    try:
        pe = pefile.PE(file_path, fast_load=True)
        pe.parse_data_directories()
        deps = []
        system_dlls = get_all_system_dlls()
        for attr in ['DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT', 'DIRECTORY_ENTRY_BOUND_IMPORT']:
            for entry in getattr(pe, attr, []):
                dll = (getattr(entry, 'dll', None) or getattr(entry, 'name', b'')).decode(errors='ignore')
                if not dll.lower().endswith(('.dll', '.exe')) or (not detect_system and dll.lower() in system_dlls):
                    continue
                dep = Dependency(dll)
                dep.delay_loaded = (attr == 'DIRECTORY_ENTRY_DELAY_IMPORT')
                dep.is_system = dll.lower() in system_dlls
                dep.invalid = False
                deps.append(dep)
        pe.close()
        return deps
    except Exception:
        dep = Dependency(os.path.basename(file_path))
        dep.invalid = True
        return [dep]

@lru_cache(maxsize=1)
def get_all_system_dlls():
    dlls = set()
    for path in os.environ.get("PATH", "").split(os.pathsep):
        try:
            for name in os.listdir(path):
                if name.lower().endswith((".dll", ".exe")):
                    dlls.add(name.lower())
        except Exception:
            pass
    return dlls

def build_dependency_graph(root_files, base_dir, executor, detect_system=False, verbose=False):
    graph = DependencyGraph()
    visited, future_to_dep, dep_objects = set(), {}, {}
    system_dlls = get_all_system_dlls()
    pbar = tqdm(total=0, desc="Resolving dependencies", unit="file", dynamic_ncols=True)

    def get_or_create(name):
        if name not in dep_objects:
            dep = Dependency(name)
            path = os.path.join(base_dir, name)
            dep.missing = not os.path.exists(path) and name.lower() not in system_dlls
            dep_objects[name] = dep
        return dep_objects[name]

    def submit(dep):
        if dep in visited or dep.missing:
            return
        visited.add(dep)
        future = executor.submit(parse_file_for_dependencies, (os.path.join(base_dir, dep.name), detect_system))
        future_to_dep[future] = dep
        pbar.total += 1
        pbar.refresh()
        if verbose:
            print(f"[DEBUG] Submitting: {dep.name}")

    for name in root_files:
        submit(get_or_create(name))

    while future_to_dep:
        for future in as_completed(list(future_to_dep)):
            parent = future_to_dep.pop(future)
            try:
                children = future.result()
            except Exception as e:
                children = []
                if verbose:
                    print(f"[ERROR] Failed to parse {parent.name}: {e}")
            for child in children:
                existing = get_or_create(child.name)
                existing.delay_loaded |= child.delay_loaded
                existing.is_system |= child.is_system
                graph.add_edge(parent, existing)
                submit(existing)
            pbar.update(1)
            break

    pbar.close()
    return graph

def build_dependency_graph_for_file(file_path, base_dir, executor, detect_system=False, verbose=False):
    return build_dependency_graph([os.path.basename(file_path)], base_dir, executor, detect_system, verbose)

def build_dependency_graph_for_dir(base_dir, executor, detect_system=False, verbose=False):
    files = [e.name for e in os.scandir(base_dir) if e.is_file() and e.name.lower().endswith((".dll", ".exe"))]
    return build_dependency_graph(files, base_dir, executor, detect_system, verbose)

def report_unused_files(graph, base_dir):
    used = {node.name for node in graph.nodes}
    present = {e.name for root, _, files in os.walk(base_dir)
        for e in [type('obj', (), {'name': f}) for f in files]
        if e.name.lower().endswith((".dll", ".exe"))}
    unused = sorted(present - used)
    print("Unused files:" if unused else "No unused files.")
    for f in unused:
        print(f"  {f}")

def print_missing(graph):
    missing = [node for node in graph.nodes if node.missing]
    if not missing:
        print("No missing dependencies.")
        return

    print("Missing dependencies:")
    for node in sorted(missing, key=lambda x: x.name.lower()):
        print(f"❌ {node.name}")
        parents = graph.parents.get(node, [])
        for p in parents:
            print(f"    ↳ Required by: {p.name}")

def print_invalid(graph):
    invalid = [node for node in graph.nodes if node.invalid]
    if not invalid:
        print("No invalid files.")
        return

    print("Invalid files (failed to parse):")
    for node in sorted(invalid, key=lambda x: x.name.lower()):
        print(f"❗ {node.name}")
        children = graph.children.get(node, [])
        if children:
            for c in children:
                print(f"    ↳ Tried to load: {c.name}")
        else:
            print(f"    ↳ No dependencies parsed.")

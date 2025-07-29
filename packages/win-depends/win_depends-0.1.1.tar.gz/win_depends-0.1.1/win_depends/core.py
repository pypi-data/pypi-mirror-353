import os
import shutil
from collections import defaultdict
from tqdm import tqdm
import concurrent.futures
import pefile
from functools import lru_cache

def get_env_paths():
    paths = set()
    for p in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isdir(p):
            paths.add(os.path.normcase(os.path.abspath(p)))
    return paths

def is_valid_dependency(filename):
    return filename.lower().endswith(".dll") or filename.lower().endswith(".exe")

def is_system_dll(filename):
    name = filename.lower()
    for path in get_env_paths():
        candidate = os.path.join(path, name)
        if os.path.isfile(candidate):
            return True
    return False

@lru_cache(maxsize=2048)
def get_cached_dependents(file_path, ignore_system, local_file_set_key, detect_system):
    return tuple(get_dependents_uncached(file_path, ignore_system, local_file_set_key, detect_system))

def get_dependents_uncached(file_path, ignore_system, local_file_set_key, detect_system):
    try:
        pe = pefile.PE(file_path, fast_load=True)
        pe.parse_data_directories()
        deps = set()
        for attr in ['DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT', 'DIRECTORY_ENTRY_BOUND_IMPORT']:
            entries = getattr(pe, attr, [])
            for entry in entries:
                dll = (getattr(entry, 'dll', None) or getattr(entry, 'name', b'')).decode(errors='ignore')
                if is_valid_dependency(dll) and not (ignore_system and is_system_dll(dll)):
                    deps.add(dll)
        return list(deps)
    except Exception:
        return []

def get_dependents(file_path, ignore_system=True, local_file_set=None, detect_system=False):
    key = frozenset(local_file_set or [])
    return list(get_cached_dependents(file_path, ignore_system, key, detect_system))

def build_dependency_map_for_dir(base_dir, local_file_set, executor, ignore_system=True, detect_system=False):
    dep_map = defaultdict(list)
    def analyze_file(file):
        full_path = os.path.join(base_dir, file)
        deps = get_dependents(full_path, ignore_system=ignore_system, local_file_set=local_file_set, detect_system=detect_system)
        return file, deps

    files = [entry.name for entry in os.scandir(base_dir)
        if entry.is_file() and entry.name.lower().endswith((".dll", ".exe"))]

    futures = {executor.submit(analyze_file, file): file for file in files}
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Analyzing files", unit="file"):
        file, deps = future.result()
        dep_map[file] = deps
    return dep_map

def build_dependency_map_for_file(file_path, base_dir, local_file_set, executor, ignore_system=True, detect_system=False):
    dep_map = defaultdict(list)
    visited = set()
    futures = {}

    def submit(file):
        if file in visited or file not in local_file_set:
            return
        visited.add(file)
        full_path = os.path.join(base_dir, file)
        futures[file] = executor.submit(get_dependents, full_path, ignore_system, local_file_set, detect_system)

    root_file = os.path.basename(file_path)
    submit(root_file)

    with tqdm(total=1, desc="Resolving dependencies", unit="file") as pbar:
        while futures:
            done_files = list(futures.keys())
            for file in done_files:
                future = futures.pop(file)
                deps = future.result()
                dep_map[file] = deps
                for dep in deps:
                    if dep not in visited and dep in local_file_set:
                        submit(dep)
                        pbar.total += 1
                        pbar.refresh()
                pbar.update(1)

    return dep_map

@lru_cache(maxsize=2)
def get_all_present_files(base_dir):
    present = set()
    for root, _, files in os.walk(base_dir):
        for name in files:
            if name.lower().endswith((".dll", ".exe")):
                present.add(name)
    return present

def report_missing_files(dep_map, base_dir, local_file_set, detect_system=False):
    all_required = set()
    for deps in dep_map.values():
        all_required.update(deps)

    present_files = get_all_present_files(base_dir)

    missing = sorted(
        dep for dep in (all_required - present_files)
        if not is_system_dll(dep)
    )

    if not missing:
        print("No missing dependencies.")
    else:
        print("Missing dependencies:")
        for f in missing:
            print(f"  {f}")

    return set(missing)

def report_unused_files(dep_map, base_dir):
    required = set()
    for deps in dep_map.values():
        required.update(deps)
    used = required.union(dep_map.keys())

    present_files = get_all_present_files(base_dir)
    unused = sorted(present_files - used)

    if not unused:
        print("No unused files.")
    else:
        print("Unused files:")
        for f in unused:
            print(f"  {f}")

def print_tree(dep_map, max_depth=None, missing_set=None, local_file_set=None):
    def recurse(file, prefix="", is_last=True, depth=0, path=None):
        if path is None:
            path = set()
        connector = "└── " if is_last else "├── "
        label = file
        is_circular = file in path
        if is_circular:
            label += " 🔁"
        if missing_set and file in missing_set:
            label += " ❌"
        print(f"{prefix}{connector}{label}")
        if is_circular or (max_depth is not None and depth >= max_depth):
            return
        path.add(file)
        children = [c for c in dep_map.get(file, []) if c != file]
        for idx, dep in enumerate(children):
            last = idx == len(children) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            recurse(dep, new_prefix, last, depth + 1, path)
        path.remove(file)

    roots = list(dep_map.keys())
    for idx, root in enumerate(roots):
        recurse(root, "", idx == len(roots) - 1)

def export_dot(dep_map):
    lines = ["digraph G {"]
    for src, deps in dep_map.items():
        for dep in deps:
            lines.append(f'    "{src}" -> "{dep}";')
    lines.append("}")
    return "\n".join(lines)

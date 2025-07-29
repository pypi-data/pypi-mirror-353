import os
from collections import defaultdict
from tqdm import tqdm
import pefile
from functools import lru_cache
from concurrent.futures import as_completed


def get_env_paths():
    paths = set()
    for p in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isdir(p):
            paths.add(os.path.normcase(os.path.abspath(p)))
    return paths


@lru_cache(maxsize=1024)
def is_system_dll(filename):
    name = filename.lower()
    for path in get_env_paths():
        candidate = os.path.join(path, name)
        if os.path.isfile(candidate):
            return True
    return False


def is_valid_dependency(filename):
    return filename.lower().endswith(".dll") or filename.lower().endswith(".exe")


def get_dependents_uncached(file_path, detect_system):
    try:
        pe = pefile.PE(file_path, fast_load=True)
        pe.parse_data_directories()
        deps = set()
        for attr in ['DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT', 'DIRECTORY_ENTRY_BOUND_IMPORT']:
            entries = getattr(pe, attr, [])
            for entry in entries:
                dll = (getattr(entry, 'dll', None) or getattr(entry, 'name', b'')).decode(errors='ignore')
                # 首先需要是一个合法的动态库
                if not is_valid_dependency(dll):
                    continue
                # 其次当不检测系统文件时, 如果目标是系统文件则跳过
                if not detect_system and is_system_dll(dll):
                    continue
                # 如果检测都通过了, 那么就添加到依赖列表中
                deps.add(dll)
        return list(deps)
    except Exception:
        return []


@lru_cache(maxsize=None)
def get_dependents_cached(file_path, detect_system):
    return get_dependents_uncached(file_path, detect_system)


def build_dependency_map(root_files, base_dir, executor, detect_system=False, verbose=False):
    dep_map = defaultdict(list)
    visited = set()
    futures = {}
    path_cache = {}

    def submit(file):
        if file in visited:
            return
        visited.add(file)
        if file not in path_cache:
            path_cache[file] = os.path.join(base_dir, file)
        full_path = path_cache[file]
        if verbose:
            print(f"[DEBUG] Submitting: {file}")
        futures[file] = executor.submit(get_dependents_cached, full_path, detect_system)

    for file in root_files:
        submit(file)

    with tqdm(total=len(futures), desc="Resolving dependencies", unit="file") as pbar:
        processed = 0
        while futures:
            futures_copy = dict(futures)
            futures.clear()

            for future in as_completed(futures_copy.values()):
                file = next(f for f, fut in futures_copy.items() if fut == future)
                try:
                    deps = future.result()
                except Exception as e:
                    deps = []
                    if verbose:
                        print(f"[ERROR] Failed to parse {file}: {e}")

                dep_map[file] = deps
                if verbose and deps:
                    print(f"[DEBUG] {file} -> {len(deps)} deps")

                for dep in deps:
                    if dep not in visited:
                        submit(dep)

                processed += 1
                pbar.update(1)

    return dep_map


def build_dependency_map_for_file(file_path, base_dir, executor, detect_system=False, verbose=False):
    root_file = os.path.basename(file_path)
    return build_dependency_map([root_file], base_dir, executor, detect_system, verbose)


def build_dependency_map_for_dir(base_dir, executor, detect_system=False, verbose=False):
    files = [
        entry.name for entry in os.scandir(base_dir)
        if entry.is_file() and entry.name.lower().endswith((".dll", ".exe"))
    ]
    return build_dependency_map(files, base_dir, executor, detect_system, verbose)


@lru_cache(maxsize=2)
def get_all_present_files(base_dir):
    present = set()
    for root, _, files in os.walk(base_dir):
        for name in files:
            if name.lower().endswith((".dll", ".exe")):
                present.add(name)
    return present


def report_missing_files(dep_map, base_dir):
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


def print_tree(dep_map, max_depth=None, missing_set=None):
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

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from .core import (
    build_dependency_map_for_dir,
    build_dependency_map_for_file,
    report_missing_files,
    report_unused_files,
    print_tree,
    export_dot
)

def main():
    parser = argparse.ArgumentParser(description="Analyze DLL/EXE dependencies.")
    parser.add_argument("target", help="Target DLL/EXE file or directory.")
    parser.add_argument("--tree", nargs="?", const=-1, type=int, metavar="LEVEL",
                        help="Print dependency tree up to specified depth (default: unlimited).")
    parser.add_argument("--graph", action="store_true", help="Print dependency graph in DOT format.")
    parser.add_argument("--dot", metavar="FILENAME", help="Write DOT graph to file.")
    parser.add_argument("--check-missing", action="store_true", help="Check for missing dependencies.")
    parser.add_argument("--check-unused", action="store_true", help="Check for unused local DLL/EXE files.")
    parser.add_argument("--detect-system", action="store_true",
                        help="Analyze system DLLs (default: off; only analyzes files in current directory).")

    args = parser.parse_args()

    target = args.target
    is_dir = os.path.isdir(target)
    is_file = os.path.isfile(target)

    if not is_dir and not (is_file and target.lower().endswith((".dll", ".exe"))):
        print(f"Error: '{target}' is not a valid DLL/EXE file or directory.")
        sys.exit(1)

    base_dir = target if is_dir else os.path.dirname(os.path.abspath(target))
    file_set = {
        f for f in os.listdir(base_dir)
        if f.lower().endswith((".dll", ".exe")) and os.path.isfile(os.path.join(base_dir, f))
    }

    ignore_system = not args.detect_system

    with ThreadPoolExecutor(max_workers=8) as executor:
        if is_dir:
            dep_map = build_dependency_map_for_dir(base_dir, file_set, executor,
                                                    ignore_system=ignore_system,
                                                    detect_system=args.detect_system)
        else:
            dep_map = build_dependency_map_for_file(target, base_dir, file_set, executor,
                                                    ignore_system=ignore_system,
                                                    detect_system=args.detect_system)

    print(f"Analyzing dependencies in: {base_dir}")

    missing = set()
    if args.check_missing or args.tree is not None:
        missing = report_missing_files(dep_map, base_dir, local_file_set=file_set, detect_system=args.detect_system)

    if args.check_unused:
        report_unused_files(dep_map, base_dir)

    if args.tree is not None:
        max_depth = None if args.tree == -1 else args.tree
        print_tree(dep_map, max_depth=max_depth, missing_set=missing, local_file_set=file_set)

    elif args.graph:
        dot = export_dot(dep_map)
        if args.dot:
            with open(args.dot, "w", encoding="utf-8") as f:
                f.write(dot)
            print(f"DOT graph written to: {args.dot}")
        else:
            print(dot)

if __name__ == "__main__":
    main()
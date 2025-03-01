#!/usr/bin/env python3

import os
import sys
import subprocess
from collections import defaultdict, deque


def get_std_symbols() -> list[str]:
    std_symbols = list()
    std_libs = [
        "/usr/lib32/libc.so.6",  # glibc
        "/usr/lib32/libm.so.6",  # math library
    ]
    for lib in std_libs:
        result = subprocess.run(
            # -D, --dynamic: Display the dynamic symbols rather than the normal symbols.  This is only meaningful for dynamic objects, such as certain types of shared libraries.
            # -g, --extern-only: Display only external symbols.
            ["nm", "--dynamic", "--extern-only", lib],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) == 3:
                _, symbol_type, symbol_name = parts
                # D: (global symbol) The symbol is in the initialized data section.
                # T: (global symbol) The symbol is in the text (code) section.
                # i: For PE format files this indicates that the symbol is in a section specific to the implementation of DLLs.
                # W: (global symbol) The  symbol  is  a weak symbol that has not been specifically tagged as a weak object symbol.
                if symbol_type in ["D", "T", "i", "W"]:
                    symbol_name = symbol_name.split("@")[0]
                    std_symbols.append(symbol_name)

    return std_symbols


def get_symbols(library: str) -> tuple[list[str], list[str]]:
    result = subprocess.run(
        # --extern-only: Display only external symbols.
        ["nm", "--extern-only", library],
        capture_output=True,
        text=True,
        check=True,
    )
    defined_symbols = list()
    undefined_symbols = list()
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2:
            symbol_type, symbol_name = parts
            if symbol_type == "U":
                undefined_symbols.append(symbol_name)
            else:
                defined_symbols.append(symbol_name)
        elif len(parts) == 3:
            _, symbol_type, symbol_name = parts
            if symbol_type == "U":
                undefined_symbols.append(symbol_name)
            else:
                defined_symbols.append(symbol_name)

    # remove self-references
    undefined_symbols = [
        symbol for symbol in undefined_symbols if symbol not in defined_symbols
    ]

    return defined_symbols, undefined_symbols


def list_libraries(directory: str, symbols: list[str]):
    libraries = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".a"):
                file_path = os.path.join(root, file)
                libraries.append(file_path)

    print(f"found {len(libraries)} libraries:")
    for i, cur_lib in enumerate(libraries):
        print(f"[{i}]: {cur_lib}")

    # key: library path
    # value: list of undefined symbols
    undefined_symbols = dict()
    # key: library path
    # value: list of defined symbols
    defined_symbols = dict()
    for cur_lib in libraries:
        defined, undefined = get_symbols(cur_lib)
        defined_symbols[cur_lib] = defined
        undefined_symbols[cur_lib] = undefined

    std_symbols = get_std_symbols()

    # key: library
    # value: list of libraries that the key library depends on
    dependencies = dict()

    for cur_lib, cur_symbols in undefined_symbols.items():
        for symbol in cur_symbols:
            found = False
            for other_library, other_symbols in defined_symbols.items():
                if symbol in other_symbols:
                    dependencies.setdefault(cur_lib, set()).add(other_library)
                    found = True
            if not found:
                if symbol not in std_symbols:
                    # found an undefined symbol
                    pass

    for i, cur_lib in enumerate(libraries):
        # print(f"[{i}]: {cur_lib}")
        if cur_lib in dependencies:
            # print(f"  depends on:")
            sorted_dependencies = list()
            for j, lib in enumerate(libraries):
                if lib in dependencies[cur_lib]:
                    sorted_dependencies.append((j, lib))

            for id, dep in sorted(sorted_dependencies):
                # print(f"    [{id}]: {dep}")
                pass

    sorted_libraries = topological_sort(libraries, dependencies)
    print("libraries in dependency order: (later libraries depend on earlier libraries)")
    for lib in sorted_libraries:
        print(lib)


def topological_sort(libraries, dependencies):
    # key: library
    # value: indegree
    indegrees = defaultdict(int)
    for lib in libraries:
        indegrees[lib] = 0

    for lib, deps in dependencies.items():
        for dep in deps:
            indegrees[dep] += 1

    queue = deque()
    for lib, indegree in indegrees.items():
        if indegree == 0:
            queue.append(lib)

    sorted_libraries = list()
    while queue:
        cur_lib = queue.popleft()
        sorted_libraries.append(cur_lib)
        if cur_lib in dependencies:
            for dep in dependencies[cur_lib]:
                indegrees[dep] -= 1
                if indegrees[dep] == 0:
                    queue.append(dep)

    # reverse the order
    sorted_libraries = sorted_libraries[::-1]

    return sorted_libraries


if __name__ == "__main__":
    # Usage: ./xc_list_libraries.py <dir> [symbol_a] [symbol_b] ...

    directory = "."
    if len(sys.argv) >= 2:
        directory = sys.argv[1]
    symbols = sys.argv[2:]

    list_libraries(directory, symbols)

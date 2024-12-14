#!/usr/bin/env python3
import json

import xiaochen_py


COMPILE_COMMANDS_FILE = "compile_commands.json"


def generate():
    # use a temporary output_base avoid discarding analysis cache
    # ref:
    # https://bazel.build/advanced/performance/iteration-speed
    output_base = "/tmp/hedron_compile_commands"
    xiaochen_py.run_command(
        f"bazel --output_base={output_base} run @hedron_compile_commands//:refresh_all"
    )


def sort():
    origin = xiaochen_py.get_file_info(COMPILE_COMMANDS_FILE)

    with open(COMPILE_COMMANDS_FILE, "r") as file:
        data = json.load(file)

    sorted_data = sorted(data, key=lambda x: x["file"])

    with open(COMPILE_COMMANDS_FILE, "w") as file:
        json.dump(sorted_data, file, indent=2)

    new_info = xiaochen_py.get_file_info(COMPILE_COMMANDS_FILE)
    print(f"origin file size: {origin.size}, new file size: {new_info.size}")

    print(
        f"sorted compile_commands.json has been written to {COMPILE_COMMANDS_FILE} with {len(sorted_data)} entries"
    )


if __name__ == "__main__":
    # generate()

    # It reads the compile_commands.json file in the current directory
    # and sorts it by "file" key.
    sort()

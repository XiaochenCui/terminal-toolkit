#!/usr/bin/env python3

import logging
import re

import xiaochen_py

MARK = "[com.google.devtools.build.lib.server.GrpcServerImpl.executeCommand]"


def run():
    output, exit_code = xiaochen_py.run_command("bazel info server_log")
    if exit_code != 0:
        logging.error("Failed to get bazel server log")
        return

    server_log_path = output.decode("utf-8").strip()

    file = open(server_log_path, "r")
    lines = file.readlines()
    lines = [l for l in lines if MARK in l]

    bazel_commands = []
    for line in lines:
        bazel_commands.append(BazelCommands(line))

    # filter 'build', 'test', 'run' commands
    build_commands = [c for c in bazel_commands if c.entry in ["build", "test", "run"]]
    if not build_commands:
        logging.error("No build commands found")
        return
    last_command = build_commands[-1]
    logging.debug(f"entry: {last_command.entry}")
    logging.debug(f"client_env: {last_command.client_env}")
    logging.debug(f"server_args: {last_command.server_args}")
    logging.debug(f"target_args: {last_command.target_args}")


class BazelCommands:
    entry: str
    server_args: list[str]
    # store client env in a separate attribute since it's too long
    client_env: dict[str, str]
    # args that passed to the target binary
    target_args: list[str]
    # for debugging
    primitive_args: str

    def __init__(self, full_command: str):
        parts = full_command.split(MARK)
        if len(parts) != 2:
            logging.error(f"failed to split entry: {full_command}")
            raise ValueError

        all_args = parts[1].strip()
        if all_args[0] == "[" and all_args[-1] == "]":
            # remove '[' and ']' from the string
            all_args = all_args[1:-1]
            all_args = all_args.split(", ")
            self.primitive_args = all_args
        else:
            logging.error(
                f"failed to parse entry: {full_command}, all_args: {all_args}"
            )
            raise ValueError

        self.server_args = []
        self.target_args = []
        self.client_env = {}

        client_args_start = False
        for i, word in enumerate(all_args):
            if i == 0:
                self.entry = word
                continue

            # word:
            # --client_env=GIT_ASKPASS=__private_value_removed__
            # key: GIT_ASKPASS
            # value: __private_value_removed__
            if word.startswith("--client_env"):
                pattern = re.compile(r"--client_env=(.*)=(.*)")
                match = pattern.match(word)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    self.client_env[key] = value
                else:
                    logging.error(f"failed to parse client env: {word}")
                    raise ValueError
                continue

            if word == "--":
                client_args_start = True
                continue

            if client_args_start:
                self.target_args.append(word)
            else:
                self.server_args.append(word)


if __name__ == "__main__":
    run()

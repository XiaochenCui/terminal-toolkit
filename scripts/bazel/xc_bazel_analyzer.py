#!/usr/bin/env python3

import datetime
import logging
import re

import xiaochen_py


REGISTER_MARK = "[com.google.devtools.build.lib.server.CommandManager.registerCommand]"
EXECUTE_MARK = "[com.google.devtools.build.lib.server.GrpcServerImpl.executeCommand]"


def run():
    output, exit_code = xiaochen_py.run_command(
        "bazel info server_log", slient=True, stream_output=False
    )
    if exit_code != 0:
        logging.error("Failed to get bazel server log")
        return

    server_log_path = output.decode("utf-8").strip()

    file = open(server_log_path, "r")
    lines = file.readlines()

    command_logs = []
    current_log = []
    for line in lines:
        if REGISTER_MARK in line:
            if current_log:
                command_logs.append(current_log)
            current_log = []
        current_log.append(line)
    # append the last log
    command_logs.append(current_log)

    bazel_commands = []
    for command_log in command_logs:
        try:
            bazel_commands.append(BazelCommand(command_log))
        except ValueError:
            # ignore the invalid command
            continue

    # filter 'build' commands
    build_commands = [c for c in bazel_commands if c.entry in ["build"]]
    if not build_commands:
        logging.error("No build commands found")
        return
    last_command = build_commands[-1]

    # logging.debug(f"entry: {last_command.entry}")
    # logging.debug(f"client_env: {last_command.client_env}")
    # logging.debug(f"server_args: {last_command.server_args}")
    # logging.debug(f"target_args: {last_command.target_args}")
    # logging.debug(f"timestamp: {last_command.timestamp.astimezone()}")

    target = ""
    for arg in last_command.server_args:
        if not arg.startswith("--"):
            target = arg
            break

    print(f"target: {target}")

    if "--sandbox_debug" not in last_command.server_args:
        logging.error(
            "option '--sandbox_debug' not found, please rebuild the target with '--sandbox_debug'"
        )
        return

    for exception in last_command.exceptions:
        parse_exception(exception)


def parse_exception(exception: str):
    lines = exception.split("\n")

    # filter "SpawnExecException"
    if len(lines) < 1 or "SpawnExecException" not in lines[0]:
        return

    for line in lines:
        pattern = re.compile(r"^\s+\S+process-wrapper (.*)")
        match = pattern.match(line)
        if match:
            all_args = match.group(1)
            all_args = all_args.split(" ")

            compiler_args_start = False
            warapper_args = []
            compiler = ""
            compiler_args = []
            for arg in all_args:
                # strip single quote
                if arg.startswith("'") and arg.endswith("'"):
                    arg = arg[1:-1]

                if compiler_args_start:
                    compiler_args.append(arg)
                else:
                    if arg.startswith("--"):
                        warapper_args.append(arg)
                    else:
                        compiler = arg
                        compiler_args_start = True

            print(f"compiler: {compiler}")
            print(f"compiler_args: {compiler_args}")
            print(f"warapper_args: {warapper_args}")


class BazelCommand:
    entry: str
    server_args: list[str]
    # store client env in a separate attribute since it's too long
    client_env: dict[str, str]
    # args that passed to the target binary
    target_args: list[str]
    # for debugging
    primitive_args: list[str]
    exec_command: str
    command_log: str
    timestamp: datetime
    exceptions: list[str]

    def __init__(self, command_log: str):
        # validate the command_log
        register_lines = [line for line in command_log if REGISTER_MARK in line]
        execute_lines = [line for line in command_log if EXECUTE_MARK in line]
        if len(register_lines) != 1 or len(execute_lines) != 1:
            raise ValueError(
                "Invalid command log: must contain exactly one REGISTER and one EXECUTE line"
            )
        execute_line = execute_lines[0]

        self.exec_command = execute_line
        self.command_log = command_log

        # parse the timestamp
        # 241208 15:02:50.151:I 1408

        pattern = re.compile(r"(\d{6} \d{2}:\d{2}:\d{2}.\d{3}):I \d+")
        match = pattern.match(execute_line)
        if not match:
            logging.error(f"failed to match timestamp: {execute_line}")
            raise ValueError
        self.timestamp = datetime.datetime.strptime(
            match.group(1), "%y%m%d %H:%M:%S.%f"
        )
        self.timestamp = self.timestamp.replace(tzinfo=datetime.timezone.utc)

        parts = execute_line.split(EXECUTE_MARK)
        if len(parts) != 2:
            logging.error(f"failed to split entry: {execute_line}")
            raise ValueError

        all_args = parts[1].strip()
        if all_args[0] == "[" and all_args[-1] == "]":
            # remove '[' and ']' from the string
            all_args = all_args[1:-1]
            all_args = all_args.split(", ")
            self.primitive_args = all_args
        else:
            logging.error(f"failed to parse entry: {command_log}, all_args: {all_args}")
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

        self.exceptions = []
        in_exception = False
        current_exception = []
        for line in command_log:
            if "Caused by:" in line:
                in_exception = True
                current_exception.append(line)
                continue

            if in_exception:
                if line.startswith(" "):
                    current_exception.append(line)
                else:
                    self.exceptions.append("\n".join(current_exception))
                    current_exception = []
                    in_exception = False


if __name__ == "__main__":
    run()

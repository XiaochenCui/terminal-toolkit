# Usage:
# 1. Put the parent directory's path in the PYTHONPATH environment variable.
# 2. Import it using "import xiaochen_py".

import datetime
import io
import json
import os
import re
import subprocess
import sys
import threading
import time
from typing import Optional, Tuple
from io import BufferedWriter
from typing import List, IO
import logging
import signal


DRY_RUN = False


# Configure the logging system
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Set the format of the log
    stream=sys.stdout,  # Ensure it logs to stdout
)


def tee_print(input_str: str, writers: List[IO]):
    """
    Write the given string to multiple writers simultaneously.

    Args:
    - input_str: The string to be written to the writers.
    - writers: A list of file-like objects (e.g., sys.stdout, file, BytesIO) to write the output to.
    """
    if not input_str.endswith("\n"):
        input_str += "\n"

    for writer in writers:
        if isinstance(writer, io.TextIOWrapper):
            writer.write(input_str)
        else:
            # convert the str to bytes for binary writers
            encoded_line = input_str.encode("utf-8")
            writer.write(encoded_line)
        writer.flush()


def tee_output(process, writers):
    """
    Capture the subprocess output, write it to multiple writers simultaneously.

    Args:
    - process: The subprocess.Popen object.
    - writers: A list of file-like objects (e.g., sys.stdout, file, BytesIO) to write the output to.
    """
    for line in iter(process.stdout.readline, b""):
        for writer in writers:
            if isinstance(writer, io.TextIOWrapper):
                # print(f"type of writer: {type(writer)}")
                writer.write(line.decode("utf-8"))
            else:
                writer.write(line)
            writer.flush()  # Ensure the output appears immediately


def run_command(
    command: str,
    include_stderr: bool = True,
    log_path: Optional[str] = None,
    stream_output: bool = True,
    kill_on_output: Optional[str] = None,
    raise_on_failure: bool = True,
    slient: bool = False,
    work_dir: Optional[str] = None,
) -> Tuple[bytes, int]:
    """
    Run a shell command and return its output and exit code.

    Args:
        command (str): The shell command to execute.
        include_stderr (bool, optional): If True, stderr is included in the output. Defaults to True.
        log_path (Optional[str], optional): The file path where output will be written in real-time. If None, no file is written.
                                               If the file exists, it will be overwritten. Defaults to None.
        stream_output (bool, optional): If True, streams the output to stdout while executing. Defaults to False.
        kill_on_output (Optional[str], optional): If the given string is found in the output, the process will be killed after 1 second.
                                                 Defaults to None.
        raise_on_failure: Throw an exception when the command exit with a non-zero exit code.

    Returns:
        Tuple[str, int]: A tuple containing the output of the command as a string and the exit code of the process.
    """
    original_dir = os.getcwd()

    if work_dir:
        os.chdir(work_dir)

    if DRY_RUN:
        print(f"(dry run) command: {command}")
        os.chdir(original_dir)
        return bytes(), 0

    if not slient:
        print(f"running command: {command}")

    start_time = time.time()

    stderr_target = None
    if include_stderr:
        stderr_target = subprocess.STDOUT

    # explaination of args:
    # - "shell=True" makes us can use a string for "command", a list of string
    #   must be used otherwise.
    # - "text=False" makes the output as bytes, which is required by api
    #   "writer.write"
    # - "bufsize=1000" makes the output got buffered (don't set bufsize=1, which
    #   set the buffer mode to "line buffer" and not avaliable for bytes output)
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=stderr_target,
        text=False,
        bufsize=1000,
    )

    writers = []
    if stream_output:
        writers.append(sys.stdout.buffer)
    if log_path:
        f = open(log_path, "w")
        print(f"running command: {command}", file=f)
        writers.append(f)
    buffer = io.BytesIO()
    writer = BufferedWriter(buffer, buffer_size=1000)
    writers.append(writer)

    # Create a thread to handle the tee output
    thread = threading.Thread(target=tee_output, args=(process, writers))
    thread.start()

    # Wait for the subprocess to finish
    process.wait()

    # Ensure the thread finishes
    thread.join()

    duration = time.time() - start_time
    if not slient:
        print(f"command finished in {duration:.2f} seconds.")

    if raise_on_failure and process.returncode != 0:
        logging.error(f"command output: {buffer.getvalue()}")
        raise subprocess.CalledProcessError(
            returncode=process.returncode, cmd=command, output=buffer.getvalue()
        )

    os.chdir(original_dir)
    return buffer.getvalue(), process.returncode


class Process:
    pid: int

    def __init__(self, pid: int):
        self.pid = pid

    def exit(self):
        """
        Terminate the process.
        """
        try:
            print(f"terminating process {self.pid}")

            # the normal kill
            # os.kill(self.pid, signal.SIGTERM)

            # the force kill
            os.kill(self.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def run_background(
    command: str, log_path: Optional[str] = None, work_dir: Optional[str] = None
) -> Process:
    """
    Run a shell command in the background and return its PID.

    Args:
        command (str): The shell command to execute.
        log_path (Optional[str], optional): The file path where output will be written in real-time. If None, no file is written.
        work_dir (Optional[str], optional): The directory to run the command in. If None, uses the current directory.

    Returns:
        int: The PID of the background process.
    """
    original_dir = os.getcwd()

    if work_dir:
        os.chdir(work_dir)

    if DRY_RUN:
        print(f"(dry run) command: {command}")
        os.chdir(original_dir)
        return Process(-1)

    print(f"running command in background: {command}")
    if log_path:
        with open(log_path, "w") as log_file:
            process = subprocess.Popen(
                command, shell=True, stdout=log_file, stderr=log_file
            )
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL)

    os.chdir(original_dir)
    return Process(process.pid)


def timestamp() -> str:
    """
    Return the current timestamp that can be used in file names.
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def get_dir_size(path: str) -> int:
    """
    Return the total size of all files in the given directory.

    Args:
    """
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size


class BenchmarkRecord:
    record_time: str
    target_attributes: dict[str, object]
    test_result: dict[str, object]

    def __init__(self, **kwargs):
        self.record_time = datetime.datetime.now().isoformat()
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"{self.record_time}, {self.target_attributes}, {self.test_result}"


def dump_records(records: List[BenchmarkRecord], dir_path: str):
    records_json = json.dumps(records, default=lambda x: x.__dict__, indent=4)
    record_path = os.path.join(
        dir_path,
        f"benchmark_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )

    with open(record_path, "w") as f:
        f.write(records_json)


def get_latest_report(report_dir: str) -> str:
    report_files = os.listdir(report_dir)

    # sort by the time in the file name in descending order
    #
    # example of file name: docs/record/benchmark_20240527_220536.json
    def sort_key(x):
        result = re.findall(r"\d+_\d+", x)[0]
        tm = datetime.datetime.strptime(result, "%Y%m%d_%H%M%S")
        return tm

    report_files.sort(key=lambda x: sort_key(x), reverse=True)
    return os.path.join(report_dir, report_files[0])


def json_loader(**kwargs):
    if "record_time" in kwargs:
        return BenchmarkRecord(**kwargs)

    return kwargs

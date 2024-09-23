# Usage:
# 1. Put the parent directory's path in the PYTHONPATH environment variable.
# 2. Import it using "import xiaochen_py".

import io
import os
import subprocess
import sys
import threading
import time
from typing import Optional, Tuple
from io import BufferedWriter
from typing import List, IO


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
    stream_output: bool = False,
    kill_on_output: Optional[str] = None,
    raise_on_failure: bool = True,
    slient: bool = False,
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
    if DRY_RUN:
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

    return buffer.getvalue(), process.returncode

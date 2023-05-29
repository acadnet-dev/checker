import json
import subprocess

def subprocess_error_to_json(e: subprocess.CalledProcessError):
    return {
        "returncode": e.returncode,
        "cmd": e.cmd,
        "output": e.output.decode("utf-8")
    }
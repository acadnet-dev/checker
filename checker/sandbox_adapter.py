import requests


class SandboxAdapter:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def upload_file(self, local_file_path):
        with open(local_file_path, "rb") as f:
            return requests.post(f"{self.endpoint}/upload_file", files={"file": f})

    def run_command(self, command):
        res = requests.post(f"{self.endpoint}/run", json={"cmd": command})

        if res.status_code != 200:
            return "Error running command"
        return res.json()
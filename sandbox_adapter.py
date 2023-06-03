import requests
from config import Config
import docker
import time
from kubernetes import client, config

class SandboxCreator:
    def __init__(self):
        self.config = Config("config.json")
        if self.config.is_development():
            self.client = docker.from_env()
        else:
            pass
            # TODO: connect to k8s

    def create_sandbox(self):
        if self.config.is_development():
            container = self.client.containers.run(self.config.sandbox_container, detach=True, ports={"2999/tcp": 0})

            # wait for sandbox to start maxim 10 seconds
            for i in range(10):
                logs = container.logs().decode("utf-8")
                if "Uvicorn running" in logs:
                    break
                time.sleep(1)

            if "Uvicorn running" not in logs:
                raise Exception("Sandbox failed to start")

            return container.id
        else:
            pass
            # TODO: create sandbox in k8s

    def get_sandbox_endpoint(self, container_id):
        if self.config.is_development():
            container = self.client.containers.get(container_id)
            print(f"Launched docker sandbox on port {container.ports['2999/tcp'][0]['HostPort']} with id {container.id}")
            return f"http://localhost:{container.ports['2999/tcp'][0]['HostPort']}"
        else:
            pass

    def stop_sandbox(self, container_id):
        if self.config.is_development():
            container = self.client.containers.get(container_id)
            container.stop()
            print(f"Stopped sandbox with id {container.id}")
        else:
            pass

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
import requests
from config import Config
import docker
import time
from kubernetes import client, config
import yaml

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
            config.load_incluster_config()

            v1 = client.CoreV1Api()

            with open(path.join(path.dirname(__file__), "sandbox-cpp-deployment.yaml")) as f:
                dep = yaml.safe_load(f)

                # add random id to deployment name
                deployment_id = str(uuid.uuid4())
                deployment_name = dep["metadata"]["name"] + "-" + deployment_id
                dep["metadata"]["name"] = deployment_name

                resp = k8s_apps_v1.create_namespaced_pod(
                    body=dep, namespace="acadnet")
                print(f"Pod created with name {deployment_name}")
            
            # wait for sandbox to start maxim 10 seconds
            for i in range(10):
                resp = v1.list_namespaced_pod(
                    namespace="default", label_selector=f"app=sandbox-cpp,deployment={deployment_id}")
                if len(resp.items) > 0:
                    break
                time.sleep(1)

            return deployment_name

    def get_sandbox_endpoint(self, id):
        if self.config.is_development():
            container = self.client.containers.get(id)
            print(f"Launched docker sandbox on port {container.ports['2999/tcp'][0]['HostPort']} with id {container.id}")
            return f"http://localhost:{container.ports['2999/tcp'][0]['HostPort']}"
        else:
            pass

    def stop_sandbox(self, id):
        if self.config.is_development():
            container = self.client.containers.get(id)
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
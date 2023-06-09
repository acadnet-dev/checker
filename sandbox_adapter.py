import requests
from config import Config
import docker
import time
from kubernetes import client, config
import yaml
import uuid
from os import path
from submission_status import SubmissionStatus

class SandboxCreator:
    def __init__(self):
        self.config = Config("config.json")
        if self.config.is_development():
            self.client = docker.from_env()
        else:
            pass
            # TODO: connect to k8s

    def create_sandbox(self, status: SubmissionStatus):
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
            # run()
            config.load_incluster_config()

            v1 = client.CoreV1Api()

            with open(path.join(path.dirname(__file__), "sandbox-cpp-deployment.yaml")) as f:
                pod = yaml.safe_load(f)

                # add random id to deployment name
                pod_id = str(uuid.uuid4())
                pod_name = pod["metadata"]["name"] + "-" + pod_id
                pod["metadata"]["name"] = pod_name

                resp = v1.create_namespaced_pod(
                    body=pod, namespace="acadnet")
                print(f"Pod created with name {pod_name}")
                status.set_status(f"pod created with name {pod_name}")

            # wait for sandbox to start maxim 5 minutes (pod creation takes a while, even more if scaling up)
            # 5 minutes = 60 * 5 = 300 seconds (poll every 5 seconds 60 times)
            for i in range(60):
                pod_status = v1.read_namespaced_pod_status(pod_name, "acadnet")
                if pod_status.status.phase == "Running":
                    pod = v1.read_namespaced_pod_log(pod_name, "acadnet")
                    if "Uvicorn running" in pod:
                        break
                time.sleep(5)
                status.set_status(f"waiting for sandbox to start - pod status: {pod_status.status.phase}")

            if "Uvicorn running" not in pod:
                status.set_status("sandbox failed to start")
                raise Exception("Sandbox failed to start")
            
            return pod_name

    def get_sandbox_endpoint(self, id):
        if self.config.is_development():
            container = self.client.containers.get(id)
            print(f"Launched docker sandbox on port {container.ports['2999/tcp'][0]['HostPort']} with id {container.id}")
            return f"http://localhost:{container.ports['2999/tcp'][0]['HostPort']}"
        else:
            config.load_incluster_config()

            v1 = client.CoreV1Api()

            status = v1.read_namespaced_pod_status(id, "acadnet")
            return f"http://{status.status.pod_ip}:2999"

    def stop_sandbox(self, id):
        if self.config.is_development():
            container = self.client.containers.get(id)
            container.stop()
            print(f"Stopped sandbox with id {container.id}")
        else:
            config.load_incluster_config()

            v1 = client.CoreV1Api()

            v1.delete_namespaced_pod(id, "acadnet")
            print(f"Stopped sandbox with id {id}")

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
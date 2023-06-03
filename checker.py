from config import Config
from api import run

from kubernetes import client, config
import yaml
from os import path
import uuid
import time
import sys

if __name__ == '__main__':
    try:
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

        # wait for sandbox to start maximum 10 seconds
        for i in range(30):
            status = v1.read_namespaced_pod_status(pod_name, "acadnet")
            if status.status.phase == "Running":
                pod = v1.read_namespaced_pod_log(pod_name, "acadnet")
                if "Uvicorn running" in pod:
                    break
            time.sleep(1)
            print("Waiting for sandbox to start")

        if "Uvicorn running" not in pod:
            raise Exception("Sandbox failed to start")
        
        print("Sandbox online")
    except Exception as e:
        print(e)

    sys.stdout.flush()

    while True:
        time.sleep(1)
    
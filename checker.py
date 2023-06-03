from config import Config
from api import run

from kubernetes import client, config
import yaml
from os import path
import uuid
import time

if __name__ == '__main__':
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

    # wait for sandbox to start maxim 10 seconds
    for i in range(10):
        pod = v1.read_namespaced_pod_log(pod_name, "acadnet")
        if "Uvicorn running" in pod:
            break
        time.sleep(1)

    if "Uvicorn running" not in pod:
        raise Exception("Sandbox failed to start")
    
    print("Sandbox online")

    while True:
        time.sleep(1)
    
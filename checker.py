from config import Config
from api import run

from kubernetes import client, config
import yaml
from os import path
import uuid

if __name__ == '__main__':
    # run()
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
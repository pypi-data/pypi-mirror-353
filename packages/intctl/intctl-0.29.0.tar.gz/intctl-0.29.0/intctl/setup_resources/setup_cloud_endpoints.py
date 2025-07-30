import os
from pathlib import Path
import subprocess
import time
from intctl.status import StatusManager
from .utils import Spinner
from importlib import resources
from intctl.utils.pathing import k8s_path
from tempfile import NamedTemporaryFile



def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def setup_cloud_endpoints(cfg: dict, status: StatusManager) -> None:
    status.start("cloud_endpoints")

    project = cfg["project_id"]
    workspace = cfg["workspace_uuid"]
    service_name = f"intellithing-{workspace}.endpoints.{project}.cloud.goog"
    spec_path = k8s_path("openapi-spec.yaml")
    print(f"[DEBUG] Resolved OpenAPI spec path: {spec_path}")

    if not os.path.exists(spec_path):
        print(f"❌ OpenAPI spec not found at {spec_path}. Please create one.")
        status.fail("cloud_endpoints")
        return

    print("🛠 Enabling required APIs...")
    with Spinner("Enabling Cloud Endpoints APIs..."):
        run(f"gcloud services enable endpoints.googleapis.com servicemanagement.googleapis.com --project={project}")

    # Deploy OpenAPI spec to Cloud Endpoints
    with open(spec_path, "r") as f:
        raw_spec = f.read()
    formatted_spec = raw_spec.format(workspace=workspace, project=project)
    
    # 🚧 Debug output BEFORE writing to file
    print("------ Rendered OpenAPI Spec ------")
    print(formatted_spec)
    print("-----------------------------------")

    with NamedTemporaryFile("w", delete=False, suffix=".yaml") as temp_file:
        temp_spec_path = temp_file.name
        temp_file.write(formatted_spec)
    print(f"🚀 Deploying OpenAPI spec to Cloud Endpoints service '{service_name}'...")
    with Spinner(f"Deploying OpenAPI spec for '{service_name}'..."):
        result = run(
            f"gcloud endpoints services deploy {temp_spec_path} --project={project}"
        )

    if result.returncode != 0:
        print("❌ Failed to deploy to Cloud Endpoints:")
        print("STDOUT:\n", result.stdout.strip())
        print("STDERR:\n", result.stderr.strip())
        status.fail("cloud_endpoints")
        return

    # Confirm the service is available
    print(f"⏳ Verifying that the service '{service_name}' is active...")
    while True:
        time.sleep(10)
        with Spinner(f"Polling for Cloud Endpoints service '{service_name}'..."):
            result = run(f"gcloud endpoints services describe {service_name} --project={project}")
        if result.returncode == 0:
            print(f"✅ Cloud Endpoints service '{service_name}' is deployed and active.")
            break
        print("⏳ Waiting for Cloud Endpoints service to become active...")

    status.complete("cloud_endpoints")

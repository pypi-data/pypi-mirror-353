import subprocess
import time
from intctl.status import StatusManager
from .utils import Spinner


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def ensure_static_ip(cfg: dict, status: StatusManager):
    status.start("static_ip")
    project = cfg["project_id"]
    region = cfg["region"]
    ip_name = f"gateway-manager-ip-{cfg['workspace_uuid']}".lower()

    print(f"🔍 Checking if static IP '{ip_name}' exists...")
    result = run(f"gcloud compute addresses describe {ip_name} --region={region} --project={project}")
    if result.returncode != 0:
        print(f"📡 Reserving static IP '{ip_name}'...")
        result = run(
            f"gcloud compute addresses create {ip_name} "
            f"--region={region} --project={project} --ip-version=IPV4"
        )
        if result.returncode != 0:
            print("❌ Failed to reserve static IP.")
            print(result.stderr)
            status.fail("static_ip")
            return
        print("✅ Static IP reserved.")
    else:
        print("✅ Static IP already exists.")
    status.complete("static_ip")


def restrict_sql_access(cfg: dict, status: StatusManager):
    status.start("sql_lockdown")
    project = cfg["project_id"]
    region = cfg["region"]
    instance = f"intellithing-pg-{cfg['workspace_uuid']}".lower()
    instance = instance if instance[0].isalpha() else "pg-" + instance[:77]

    print(f"🔒 Locking down SQL instance '{instance}' to remove public access...")

    # Remove all authorized networks (public IP)
    result = run(
        f"gcloud sql instances patch {instance} --project={project} "
        f"--clear-authorized-networks"
    )
    if result.returncode != 0:
        print("❌ Failed to clear public authorized networks.")
        print(result.stderr)
        status.fail("sql_lockdown")
        return

    print("✅ Public access removed from SQL instance.")

    # Optional: Add private network if you want to assign VPC access (currently GKE can access private IPs if in same VPC)
    status.complete("sql_lockdown")

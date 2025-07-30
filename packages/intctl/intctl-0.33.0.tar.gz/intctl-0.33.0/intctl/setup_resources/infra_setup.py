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
    with Spinner(f"Checking for existing static IP '{ip_name}'..."):
        result = run(f"gcloud compute addresses describe {ip_name} --region={region} --project={project}")

    if result.returncode != 0:
        print(f"📡 Reserving static IP '{ip_name}'...")
        with Spinner(f"Creating static IP '{ip_name}'..."):
            result = run(
                f"gcloud compute addresses create {ip_name} "
                f"--region={region} --project={project}"
            )
        if result.returncode != 0:
            print("❌ Failed to reserve static IP.")
            print(result.stderr.strip())
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
    workspace = cfg["workspace_uuid"]

    # Construct resource names
    cluster_name = f"int-{workspace}".lower()
    sql_instance = f"intellithing-pg-{workspace}".lower()
    if not sql_instance[0].isalpha():
        sql_instance = "pg-" + sql_instance[:77]

    print(f"🔍 Using cluster: {cluster_name}")
    print(f"🔍 Using SQL instance: {sql_instance}")

    # Step 1: Retrieve the VPC network URI from the cluster
    print(f"🔧 Getting VPC network used by cluster '{cluster_name}'...")
    with Spinner(f"Describing GKE cluster '{cluster_name}' to get network..."):
        get_network = run(
            f"gcloud container clusters describe {cluster_name} "
            f"--region={region} --project={project} "
            f"--format='value(networkConfig.network)'"
        )

    if get_network.returncode != 0 or not get_network.stdout.strip():
        print("❌ Could not determine cluster network.")
        print(get_network.stderr.strip())
        status.fail("sql_lockdown")
        return

    vpc_uri = get_network.stdout.strip()
    network = vpc_uri.split("/")[-1]
    print(f"✅ GKE cluster is on network: {vpc_uri}")

    # Step 2: Ensure subnet has a secondary IP range for peering
    print(f"🔧 Checking if subnet 'default' has secondary range 'sql-range'...")
    with Spinner("Checking secondary range..."):
        subnet_check = run(
            f"gcloud compute networks subnets describe default "
            f"--region={region} --project={project} "
            f"--format='value(secondaryIpRanges.name)'"
        )

    if "sql-range" not in subnet_check.stdout:
        print("🆕 Adding secondary IP range 'sql-range' to subnet 'default'...")
        with Spinner("Adding secondary IP range..."):
            add_range = run(
                f"gcloud compute networks subnets update default "
                f"--region={region} --add-secondary-ranges sql-range=10.10.0.0/16 "
                f"--project={project}"
            )
        if add_range.returncode != 0:
            print("❌ Failed to add secondary IP range.")
            print(add_range.stderr.strip())
            status.fail("sql_lockdown")
            return
    else:
        print("✅ Secondary IP range 'sql-range' already exists.")

    # Step 3: Ensure VPC peering exists with Service Networking
    print(f"🔌 Ensuring VPC peering exists between '{network}' and Service Networking...")
    with Spinner(f"Creating VPC peering for '{network}'..."):
        peer_check = run(
            f"gcloud services vpc-peerings connect "
            f"--service=servicenetworking.googleapis.com "
            f"--network={network} --ranges=sql-range --project={project}"
        )
    if peer_check.returncode != 0 and "already exists" not in peer_check.stderr:
        print("⚠️ Peering may already exist or failed to create.")
        print(peer_check.stderr.strip())

    # Step 4: Remove public access from SQL
    print("🚫 Removing all public access from SQL instance...")
    with Spinner(f"Clearing authorized networks on SQL instance '{sql_instance}'..."):
        run(f"gcloud sql instances patch {sql_instance} --project={project} --clear-authorized-networks")

    # Step 5: Enable private IP if not already configured
    print("🔎 Checking if SQL has private IP enabled...")
    with Spinner(f"Describing SQL instance '{sql_instance}' for private IP..."):
        check_private = run(
            f"gcloud sql instances describe {sql_instance} --project={project} "
            f"--format='value(ipConfiguration.privateNetwork)'"
        )

    if not check_private.stdout.strip():
        print("🔐 Enabling private IP and connecting SQL to GKE VPC...")
        with Spinner(f"Patching SQL instance '{sql_instance}' to use VPC..."):
            enable_private = run(
                f"gcloud sql instances patch {sql_instance} "
                f"--project={project} --network={vpc_uri} --no-assign-ip"
            )
        if enable_private.returncode != 0:
            print("❌ Failed to enable private IP or attach to VPC.")
            print(enable_private.stderr.strip())
            status.fail("sql_lockdown")
            return
        print("✅ SQL is now private and VPC-attached.")
    else:
        print("✅ SQL already has private network configuration.")

    status.complete("sql_lockdown")

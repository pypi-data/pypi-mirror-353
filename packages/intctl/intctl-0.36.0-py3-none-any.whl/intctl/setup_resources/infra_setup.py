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

    vpc_name = f"intellithing-vpc-{workspace}".lower()
    subnet_name = f"intellithing-subnet-{workspace}".lower()

    print(f"🔍 Using cluster: {cluster_name}")
    print(f"🔍 Using SQL instance: {sql_instance}")
    print(f"🔍 Target VPC: {vpc_name}")
    print(f"🔍 Target Subnet: {subnet_name}")

    # Step 0: Ensure VPC and Subnet exist
    print(f"🔧 Checking if VPC '{vpc_name}' exists...")
    with Spinner(f"Checking VPC '{vpc_name}'..."):
        vpc_check = run(
            f"gcloud compute networks describe {vpc_name} "
            f"--project={project} --format='value(name)'"
        )

    if vpc_check.returncode != 0:
        print(f"🆕 Creating VPC '{vpc_name}'...")
        with Spinner(f"Creating VPC '{vpc_name}'..."):
            vpc_create = run(
                f"gcloud compute networks create {vpc_name} "
                f"--subnet-mode=custom --project={project}"
            )
        if vpc_create.returncode != 0:
            print("❌ Failed to create VPC.")
            print(vpc_create.stderr.strip())
            status.fail("sql_lockdown")
            return
        print("✅ VPC created.")
    else:
        print("✅ VPC already exists.")

    print(f"🔧 Checking if Subnet '{subnet_name}' exists...")
    with Spinner(f"Checking Subnet '{subnet_name}'..."):
        subnet_check = run(
            f"gcloud compute networks subnets describe {subnet_name} "
            f"--region={region} --project={project} "
            f"--format='value(name)'"
        )

    if subnet_check.returncode != 0:
        print(f"🆕 Creating Subnet '{subnet_name}'...")
        with Spinner(f"Creating Subnet '{subnet_name}'..."):
            subnet_create = run(
                f"gcloud compute networks subnets create {subnet_name} "
                f"--network={vpc_name} --region={region} "
                f"--range=10.0.0.0/16 "
                f"--secondary-range=sql-range=10.10.0.0/16 "
                f"--project={project}"
            )
        if subnet_create.returncode != 0:
            print("❌ Failed to create Subnet.")
            print(subnet_create.stderr.strip())
            status.fail("sql_lockdown")
            return
        print("✅ Subnet created.")
    else:
        print("✅ Subnet already exists.")

    network = vpc_name
    vpc_uri = f"https://www.googleapis.com/compute/v1/projects/{project}/global/networks/{vpc_name}"
    print(f"✅ Using VPC URI: {vpc_uri}")

    # Step 1: Create allocated IP range for VPC peering (if not exists)
    print("🔧 Checking if allocated IP range 'sql-range' exists for VPC peering...")
    with Spinner("Checking allocated peering range..."):
        check_range = run(
            f"gcloud compute addresses describe sql-range "
            f"--global --project={project} "
            f"--format='value(name)'"
        )

    if check_range.returncode != 0:
        print("🆕 Creating allocated IP range 'sql-range'...")
        create_range = run(
            f"gcloud compute addresses create sql-range "
            f"--global --prefix-length=16 "
            f"--description='Peering range for Cloud SQL' "
            f"--network={network} --purpose=VPC_PEERING "
            f"--project={project}"
        )
        if create_range.returncode != 0:
            print("❌ Failed to create allocated IP range for VPC peering.")
            print(create_range.stderr.strip())
            status.fail("sql_lockdown")
            return
        print("✅ Allocated IP range created.")
    else:
        print("✅ Allocated IP range 'sql-range' already exists.")

    # Step 2: Ensure VPC peering exists with Service Networking
    print(f"🔌 Ensuring VPC peering exists between '{network}' and Service Networking...")
    with Spinner(f"Creating VPC peering for '{network}'..."):
        peer_connect = run(
            f"gcloud services vpc-peerings connect "
            f"--service=servicenetworking.googleapis.com "
            f"--network={network} --ranges=sql-range --project={project}"
        )

    if peer_connect.returncode != 0 and "already exists" not in peer_connect.stderr:
        print("⚠️ Peering may already exist or failed to create.")
        print(peer_connect.stderr.strip())

    # Step 3: Poll until peering becomes ACTIVE
    print("⏳ Waiting for VPC peering to become ACTIVE...")
    for _ in range(60):  # up to 5 minutes
        time.sleep(5)
        with Spinner("Checking peering status..."):
            peer_status = run(
                f"gcloud compute networks peerings list "
                f"--network={network} --project={project} "
                f"--filter='name:servicenetworking-googleapis-com' "
                f"--format='value(state)'"
            )
        if peer_status.returncode == 0 and peer_status.stdout.strip() == "ACTIVE":
            print("✅ VPC peering is ACTIVE.")
            break
    else:
        print("❌ VPC peering did not become ACTIVE in time.")
        status.fail("sql_lockdown")
        return

    # Step 4: Remove public access from SQL
    print("✅ Removing all public access from SQL instance...")
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

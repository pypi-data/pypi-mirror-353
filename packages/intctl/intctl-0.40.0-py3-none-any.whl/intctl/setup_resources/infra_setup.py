import subprocess
import time
from intctl.status import StatusManager
from .utils import Spinner
import json

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
    sql_instance = f"intellithing-pg-{workspace}".lower()
    vpc_name = f"intellithing-vpc-{workspace}".lower()
    subnet_name = f"intellithing-subnet-{workspace}".lower()

    print(f"🔍 Using SQL instance: {sql_instance}")
    print(f"🔍 Target VPC: {vpc_name}")
    print(f"🔍 Target Subnet: {subnet_name}")

    # (VPC and Subnet creation logic is fine)
    print(f"🔧 Checking if VPC '{vpc_name}' exists...")
    with Spinner(f"Checking VPC '{vpc_name}'..."):
        vpc_check = run(f"gcloud compute networks describe {vpc_name} --project={project} --format='value(name)'")
    if vpc_check.returncode != 0:
        print(f"🆕 Creating VPC '{vpc_name}'...")
        with Spinner(f"Creating VPC '{vpc_name}'..."):
            vpc_create = run(f"gcloud compute networks create {vpc_name} --subnet-mode=custom --project={project}")
        if vpc_create.returncode != 0:
            print("❌ Failed to create VPC."); print(vpc_create.stderr.strip()); status.fail("sql_lockdown"); return
        print("✅ VPC created.")
    else:
        print("✅ VPC already exists.")

    print(f"🔧 Checking if Subnet '{subnet_name}' exists...")
    with Spinner(f"Checking Subnet '{subnet_name}'..."):
        subnet_check = run(f"gcloud compute networks subnets describe {subnet_name} --region={region} --project={project} --format='value(name)'")
    if subnet_check.returncode != 0:
        print(f"🆕 Creating Subnet '{subnet_name}'...")
        with Spinner(f"Creating Subnet '{subnet_name}'..."):
            subnet_create = run(
                f"gcloud compute networks subnets create {subnet_name} --network={vpc_name} --region={region} "
                f"--range=10.0.0.0/16 --project={project}"
            )
        if subnet_create.returncode != 0:
            print("❌ Failed to create Subnet."); print(subnet_create.stderr.strip()); status.fail("sql_lockdown"); return
        print("✅ Subnet created.")
    else:
        print("✅ Subnet already exists.")

    network = vpc_name
    vpc_uri = f"https://www.googleapis.com/compute/v1/projects/{project}/global/networks/{vpc_name}"
    print(f"✅ Using VPC URI: {vpc_uri}")

    # (Allocated IP range logic is fine)
    print("🔧 Checking if allocated IP range 'sql-range' exists for VPC peering...")
    with Spinner("Checking allocated peering range..."):
        check_range = run(f"gcloud compute addresses describe sql-range --global --project={project} --format='value(name)'")
    if check_range.returncode != 0:
        print("🆕 Creating allocated IP range 'sql-range'...")
        create_range = run(
            f"gcloud compute addresses create sql-range --global --prefix-length=16 "
            f"--description='Peering range for Cloud SQL' --network={network} --purpose=VPC_PEERING --project={project}"
        )
        if create_range.returncode != 0:
            print("❌ Failed to create allocated IP range for VPC peering."); print(create_range.stderr.strip()); status.fail("sql_lockdown"); return
        print("✅ Allocated IP range created.")
    else:
        print("✅ Allocated IP range 'sql-range' already exists.")

    # (Peering connect logic is fine)
    print(f"🔌 Ensuring VPC peering exists between '{network}' and Service Networking...")
    with Spinner(f"Connecting VPC peering for '{network}'..."):
        peering_name = f"servicenetworking-{vpc_name}"
        peer_connect = run(
            f"gcloud services vpc-peerings connect "
            f"--service=servicenetworking.googleapis.com "
            f"--network={network} --ranges=sql-range "
            f"--peering={peering_name} "
            f"--project={project}"
        )
    if peer_connect.returncode != 0 and "already exists" not in peer_connect.stderr:
        print("⚠️ Peering failed or already exists."); print(peer_connect.stderr.strip())
    else:
        print("✅ Peering connection initiated or already exists.")

    # --- THIS IS THE DEFINITIVE POLLING FIX USING JSON ---
    print("⏳ Waiting for VPC peering to become ACTIVE...")
    peering_is_active = False
    for i in range(30):  # Poll for up to 2.5 minutes
        with Spinner(f"Checking peering status (attempt {i+1}/30)..."):
            peer_status = run(
                f"gcloud compute networks peerings list "
                f"--network={network} --project={project} --format=json"
            )

        if peer_status.returncode == 0 and peer_status.stdout.strip():
            try:
                peerings_list = json.loads(peer_status.stdout)
                for peering in peerings_list:
                    if (
                        peering.get("name", "") == peering_name
                        and peering.get("state") == "ACTIVE"
                    ):
                        peering_is_active = True
                        break
            except json.JSONDecodeError:
                pass # Ignore parsing errors and retry

        if peering_is_active:
            print("\n✅ VPC peering is ACTIVE.")
            break
        
        time.sleep(5)

    if not peering_is_active:
        print("\n❌ VPC peering did not become ACTIVE in time. Check GCP console."); status.fail("sql_lockdown"); return

    # (SQL clearing is usually fast, but this is fine)
    print("🔐 Removing all public access from SQL instance...")
    with Spinner(f"Clearing authorized networks on '{sql_instance}'..."):
        run(f"gcloud sql instances patch {sql_instance} --project={project} --clear-authorized-networks")

    # (SQL private IP check is fine)
    print("🔎 Checking if SQL has private IP enabled...")
    with Spinner(f"Describing SQL instance '{sql_instance}'..."):
        check_private = run(f"gcloud sql instances describe {sql_instance} --project={project} --format='value(settings.ipConfiguration.privateNetwork)'")

    # --- THIS IS THE DEFINITIVE SQL PATCH FIX ---
    if not check_private.stdout.strip():
        print("🔐 Enabling private IP and connecting SQL to GKE VPC...")
        enable_private = run(
            f"gcloud sql instances patch {sql_instance} "
            f"--project={project} --network={vpc_uri} --no-assign-ip --async "
            f"--format='value(name)'"
        )
        if enable_private.returncode != 0:
            print("❌ Failed to start the operation to enable private IP."); print(enable_private.stderr.strip()); status.fail("sql_lockdown"); return
        
        operation_id = enable_private.stdout.strip()
        print(f"⏳ Waiting for SQL patch operation '{operation_id}' to complete...")
        with Spinner(f"Patching SQL instance '{sql_instance}'..."):
            wait_for_op = run(f"gcloud sql operations wait {operation_id} --project={project} --timeout=300")
        
        if wait_for_op.returncode != 0:
            print("\n❌ Operation to enable private IP failed or timed out."); print(f"   Check status with: gcloud sql operations describe {operation_id} --project={project}"); status.fail("sql_lockdown"); return
            
        print("\n✅ SQL is now private and VPC-attached.")
    else:
        print("✅ SQL already has a private network configuration.")

    status.complete("sql_lockdown")
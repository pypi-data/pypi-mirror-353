import subprocess
import time
import json
import typer

from intctl.status import StatusManager
from .utils import Spinner

def run(cmd: str, input: str = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, shell=True, input=input, capture_output=True, text=True
    )

def setup_https_gateway(cfg: dict, status: StatusManager):
    """
    Sets up a GKE Gateway, a Google-managed certificate via nip.io,
    and an HTTPRoute to enable HTTPS for the gateway-manager.
    """
    status.start("https_gateway")

    project = cfg["project_id"]
    region = cfg["region"]
    workspace = cfg["workspace_uuid"]
    ip_name = f"gateway-manager-ip-{workspace}".lower()
    gateway_name = f"intellithing-gateway-{workspace}".lower()
    domain = cfg.get("domain")
    
    # 1. Ensure the GKE Gateway Controller is enabled
    print("🚀 Ensuring GKE Gateway API controller is enabled...")
    with Spinner("Checking GKE Gateway addons..."):
        run(
            "gcloud container clusters update int-" + workspace.lower() +
            f" --project={project} --region={region} "
            "--update-addons=Gateway=ENABLED"
        )
    print("✅ GKE Gateway API is enabled.")

    # 2. Get the Static IP Address
    print(f"🔍 Fetching static IP address for '{ip_name}'...")
    ip_result = run(f"gcloud compute addresses describe {ip_name} --global --project={project} --format='value(address)'")
    if ip_result.returncode != 0:
        print(f"❌ Could not find static IP '{ip_name}'. Please run setup first.")
        status.fail("https_gateway", f"Static IP not found: {ip_name}")
        raise typer.Exit(1)
    
    static_ip = ip_result.stdout.strip()
    print(f"✅ Found static IP: {static_ip}")
    
    # Get the custom domain from the configuration dictionary
    if not domain:
        print(f"❌ Could not find the custom domain in the configuration. Please ensure the subdomain setup step was successful.")
        status.fail("https_gateway", "Custom domain not found in config")
        raise typer.Exit(1)
    
    print(f"✅ Using custom domain: {domain}")
    
    # ====================================================================
    # NEW: 2.5. Wait for Backend Service to be Ready
    # This new block polls for the gateway-manager Endpoints before proceeding.
    # ====================================================================
    print("🔎 Waiting for the gateway-manager backend to be ready...")
    backend_ready = False
    # 1. Start a loop that will time out after 2 minutes (12 attempts x 10 seconds).
    for i in range(12):
        with Spinner(f"Checking for active endpoints... (Attempt {i+1}/12)"):
            # 2. Run a kubectl command to get the Endpoints for the 'gateway-manager' service.
            #    We check Endpoints because they only exist if there are healthy, running pods.
            ep_result = run("kubectl get endpoints gateway-manager -n intellithing -o json")
        
        # 3. Check if the command was successful and returned a valid object.
        if ep_result.returncode == 0:
            try:
                endpoints = json.loads(ep_result.stdout)
                # 4. THE KEY CHECK: If the 'subsets' field exists and is not empty, it means
                #    the service has at least one active pod. The backend is ready.
                if endpoints.get("subsets"):
                    backend_ready = True
                    break  # Exit the loop successfully.
            except json.JSONDecodeError:
                # If the output isn't valid JSON yet, just ignore and try again.
                pass
        
        # 5. If the backend is not ready, wait 10 seconds before the next attempt.
        time.sleep(10)

    # 6. After the loop, check if the backend was ever found.
    if not backend_ready:
        # If not, print a clear error message and stop the script.
        print("\n❌ Timed out waiting for the 'gateway-manager' service to have active endpoints.")
        print("   Please ensure the gateway-manager deployment is running and healthy.")
        print("   You can check with: 'kubectl get pods -n intellithing -l app=gateway-manager'")
        status.fail("https_gateway", "Backend service not ready")
        raise typer.Exit(1)

    # 7. If the loop was successful, print a confirmation message and continue with the script.
    print("✅ Backend service is ready with active endpoints.")
    # ====================================================================
    # End of new section
    # ====================================================================

    # 3. Create the Gateway, ManagedCertificate, and HTTPRoute manifests
    # 3. Create the Gateway, ManagedCertificate, and HTTPRoute manifests
    manifests = f"""
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: {gateway_name}
  namespace: intellithing
  annotations:
    networking.gke.io/managed-certificates: {gateway_name}-cert
spec:
  gatewayClassName: gke-l7-gxlb
  listeners:
  - name: http                
    protocol: HTTP
    port: 80
    allowedRoutes:
      namespaces:
        from: All
  - name: https               
    protocol: HTTPS
    port: 443
    tls:
      mode: Terminate
      certificateRefs:
      - group: networking.gke.io
        kind: ManagedCertificate
        name: {gateway_name}-cert
    allowedRoutes:
      namespaces:
        from: All
  addresses:
  - type: NamedAddress
    value: {ip_name}
---
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: {gateway_name}-cert
  namespace: intellithing
spec:
  domains:
  - {domain}
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: gateway-manager-route
  namespace: intellithing
spec:
  parentRefs:
  - name: {gateway_name}
  hostnames:
  - "{domain}"
  rules:
  - backendRefs:
    - name: gateway-manager
      port: 80
"""


    print("☸️ Applying Kubernetes Gateway manifests...")
    with Spinner("Applying Gateway, Certificate, and Route..."):
        apply_result = run("kubectl apply -f -", input=manifests)
    
    if apply_result.returncode != 0:
        print("❌ Failed to apply Gateway manifests.")
        print(apply_result.stderr)
        status.fail("https_gateway", "kubectl apply failed")
        raise typer.Exit(1)

    print("✅ Gateway manifests applied successfully.")
    print("⏳ Waiting for certificate to be provisioned. This can take up to 15 minutes...")

    # 4. Wait for the certificate to become active
    for i in range(45): # Poll for up to 15 minutes
        with Spinner(f"Checking certificate status... (Attempt {i+1}/45)"):
            cert_status_result = run(
                f"kubectl get managedcertificate {gateway_name}-cert -n intellithing -o json"
            )
        
        if cert_status_result.returncode == 0:
            cert_status = json.loads(cert_status_result.stdout)
            status_condition = next((c for c in cert_status.get("status", {}).get("conditions", []) if c.get("type") == "Ready"), None)
            if status_condition and status_condition.get("status") == "True":
                print(f"\n🎉 Certificate is ACTIVE! Your service is available at:")
                print(f"   https://{domain}")
                status.complete("https_gateway")
                return
        
        time.sleep(20)

    print("\n❌ Certificate did not become active in time. Please check the status manually:")
    print(f"   kubectl describe managedcertificate {gateway_name}-cert -n intellithing")
    status.fail("https_gateway", "Certificate provisioning timed out")
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
    
    # 3. Ensure backend service (gateway-manager-deployment) is ready before applying manifests
    def is_service_ready():
        result = run("kubectl get endpoints gateway-manager-deployment -n intellithing -o json")
        if result.returncode != 0:
            return False
        obj = json.loads(result.stdout)
        return bool(obj.get("subsets"))

    print("⏳ Waiting for gateway-manager-deployment service to become ready...")
    for i in range(30):  # 10 minutes max
        with Spinner(f"Checking service readiness (Attempt {i+1}/30)"):
            if is_service_ready():
                print("✅ Service is ready.")
                break
        time.sleep(20)
    else:
        print("❌ Service 'gateway-manager-deployment' is not ready.")
        status.fail("https_gateway", "Service readiness timed out")
        raise typer.Exit(1)

    
  
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
      options:
        networking.gke.io/managed-certificates: {gateway_name}-cert
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
    - name: gateway-manager-deployment
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
    
    def is_gateway_ready():
        result = run(f"kubectl get gateway {gateway_name} -n intellithing -o json")
        if result.returncode != 0:
            return False
        obj = json.loads(result.stdout)
        conditions = obj.get("status", {}).get("conditions", [])
        return any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)

    def is_route_accepted():
        result = run("kubectl get httproute gateway-manager-route -n intellithing -o json")
        if result.returncode != 0:
            return False
        obj = json.loads(result.stdout)
        for parent in obj.get("status", {}).get("parents", []):
            for cond in parent.get("conditions", []):
                if cond.get("type") == "Accepted" and cond.get("status") == "True":
                    return True
        return False

    print("⏳ Waiting for Gateway and Route to be fully active...")
    for i in range(65):  # ~10 minutes max
        with Spinner(f"Checking Gateway and Route readiness (Attempt {i+1}/30)"):
            if is_gateway_ready() and is_route_accepted():
                print("✅ Gateway is Ready and Route is Accepted.")
                break
        time.sleep(20)
    else:
        print("❌ Gateway or Route not ready in time.")
        print(f"   kubectl describe gateway {gateway_name} -n intellithing")
        print("   kubectl describe httproute gateway-manager-route -n intellithing")
        status.fail("https_gateway", "Gateway or route readiness timed out")
        raise typer.Exit(1)

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
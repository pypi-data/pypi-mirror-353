from pathlib import Path
from importlib import resources

# Use once, everywhere else imports this
PACKAGE_ROOT = Path(resources.files("intctl"))   # → …/site-packages/intctl

def k8s_path(*parts: str) -> Path:
    """
    Return an absolute path inside the packaged intctl/k8s directory.
    Example: k8s_path("openapi-spec.yaml")
             k8s_path("project-manager", "deployment.yaml")
    """
    return PACKAGE_ROOT / "k8s" / Path(*parts)

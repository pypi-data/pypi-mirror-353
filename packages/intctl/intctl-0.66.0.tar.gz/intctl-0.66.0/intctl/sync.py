# intctl/sync.py

import typer
import requests
import json
from intctl.config import load_config, save_config, apply_env

# This should be configurable, but a constant is fine for now.
API_BASE_URL = "https://your-api-endpoint.com/api/v1" # <--- IMPORTANT: Change this to your actual API URL

def sync_from_api():
    """
    Fetches setup configuration from the API using a setup_uuid and saves it locally.
    """
    print("🔄 Starting sync from INTELLITHING ...")
    setup_uuid = typer.prompt("Please enter your Setup UUID")

    if not setup_uuid:
        typer.secho("Setup UUID cannot be empty.", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    endpoint = f"{API_BASE_URL}/setups/{setup_uuid}"
    
    try:
        print(f"📡 Calling INTELLITHING")
        response = requests.get(endpoint)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
    
    except requests.exceptions.RequestException as e:
        typer.secho(f"❌ call failed: {e}", fg=typer.colors.RED)
        if e.response:
            typer.secho(f"   Response: {e.response.text}", fg=typer.colors.RED)
        raise typer.Exit(1)

    api_data = response.json()
    print("✅ Successfully fetched data from API.")
    
    cfg = load_config()
    
    # Define which fields from the API response should be written to the local config
    updatable_fields = [
        "user_uuid", 
        "organization_uuid",
        "organization_name",
        "workspace_uuid",
        "region",
        "intellithing_key",
    ]

    print("📝 Updating local configuration...")
    for field in updatable_fields:
        if field in api_data and api_data[field]:
            cfg[field] = api_data[field]
            print(f"   - Set '{field}'")
            
    # Also store the setup_uuid itself for the --complete step
    cfg["setup_uuid"] = setup_uuid
    print(f"   - Set 'setup_uuid'")
    
    save_config(cfg)
    apply_env(cfg) # Apply changes to environment
    print("\n✅ Configuration has been synced and saved successfully.")


def _get_completion_payload():
    """Helper to load config and build the completion payload."""
    cfg = load_config()
    
    required_fields = [
        "setup_uuid",
        "organization_name",
        "user_uuid",
        "organization_uuid",
        "workspace_uuid",
        "region",
        "secret",
        "static_ip", 
    ]
    
    payload = {}
    missing_fields = []
    
    for field in required_fields:
        if field in cfg and cfg[field]:
            payload[field] = cfg[field]
        else:
            missing_fields.append(field)
            
    if missing_fields:
        typer.secho(f"❌ Cannot proceed. Missing required configuration: {', '.join(missing_fields)}", fg=typer.colors.RED)
        typer.secho("   Please run `intctl configure` and `intctl setup` first.", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    return payload


def post_completion_data():
    """
    Reads local config and posts completion data to the API.
    """
    print("🚀 Preparing to post completion data to IntelliThing API...")
    payload = _get_completion_payload()
    
    setup_uuid = payload.pop("setup_uuid") # The UUID goes in the URL, not the body
    endpoint = f"{API_BASE_URL}/setups/{setup_uuid}/complete"

    try:
        print(f"📡 Calling API: POST {endpoint}")
        print("   Payload:", json.dumps(payload, indent=2))
        # Assuming your API might need an auth token, e.g., from the config
        headers = {"Authorization": f"Bearer {load_config().get('intellithing_key')}"}
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        typer.secho(f"❌ API call failed: {e}", fg=typer.colors.RED)
        if e.response:
            typer.secho(f"   Response: {e.response.text}", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    print("\n✅ Successfully posted completion data to the API.")
    print("   Response:", response.text)


def show_manual_data():
    """

    Reads local config and displays completion data for manual copy-pasting.
    """
    print("📋 Completion Data for Manual Entry:")
    payload = _get_completion_payload()

    print("-" * 40)
    for key, value in payload.items():
        print(f"{key.upper():<20}: {value}")
    print("-" * 40)
    print("\nYou can now copy these values into the IntelliThing platform.")
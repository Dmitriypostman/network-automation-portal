import json
import os
from pathlib import Path

from dotenv import load_dotenv

from drivers.nxapi_driver import add_vlan_nxapi
from drivers.ssh_driver import add_vlan_ssh

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INVENTORY_FILE = BASE_DIR / "inventory.json"

CREDENTIALS = {
    "nxos_lab": {
        "username": os.getenv("NXOS_LAB_USERNAME"),
        "password": os.getenv("NXOS_LAB_PASSWORD"),
    },
    "catalyst_lab": {
        "username": os.getenv("CATALYST_LAB_USERNAME"),
        "password": os.getenv("CATALYST_LAB_PASSWORD"),
    },
}


def load_inventory():
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_device_by_name(device_name: str):
    inventory = load_inventory()
    for device in inventory.get("devices", []):
        if device.get("device_name") == device_name:
            return device
    return None


def get_credentials_for_device(device: dict):
    profile = device.get("credential_profile")

    if not profile:
        raise ValueError(f"Device '{device.get('device_name')}' has no credential_profile")

    creds = CREDENTIALS.get(profile)
    if not creds:
        raise ValueError(f"Credential profile '{profile}' not found")

    username = creds.get("username")
    password = creds.get("password")

    if not username or not password:
        raise ValueError(f"Username or password is missing for credential profile '{profile}'")

    return creds


def add_vlan_to_device_trunk(device: dict, interface_name: str, vlan_id: int):
    connection_method = device.get("connection_method", "").lower()
    creds = get_credentials_for_device(device)

    if connection_method == "nxapi":
        return add_vlan_nxapi(device, interface_name, vlan_id, creds)

    if connection_method == "ssh":
        return add_vlan_ssh(device, interface_name, vlan_id, creds)

    return False, f"Unsupported connection method: {connection_method}"
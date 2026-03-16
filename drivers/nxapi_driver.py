import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def add_vlan_nxapi(device: dict, interface_name: str, vlan_id: int, creds: dict):
    ip = device["ip_address"]
    username = creds["username"]
    password = creds["password"]

    url = f"https://{ip}/ins"

    commands = [
        f"vlan {vlan_id}",
        f"interface {interface_name}",
        f"switchport trunk allowed vlan add {vlan_id}",
    ]

    payload = {
        "ins_api": {
            "version": "1.0",
            "type": "cli_conf",
            "chunk": "0",
            "sid": "1",
            "input": " ; ".join(commands),
            "output_format": "json",
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(username, password),
            headers={"Content-Type": "application/json"},
            verify=False,
            timeout=10,
        )

        if response.status_code != 200:
            return False, (
                f"NX-API HTTP error on {device['device_name']}: "
                f"{response.status_code} - {response.text}"
            )

        return True, (
            f"VLAN {vlan_id} was added to trunk interface {interface_name} "
            f"on device {device['device_name']} via NX-API"
        )

    except Exception as e:
        return False, f"NX-API exception on {device['device_name']}: {str(e)}"
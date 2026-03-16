from netmiko import ConnectHandler


def add_vlan_ssh(device: dict, interface_name: str, vlan_id: int, creds: dict):
    device_params = {
        "device_type": device.get("platform", "cisco_ios"),
        "host": device["ip_address"],
        "username": creds["username"],
        "password": creds["password"],
    }

    commands = [
        f"vlan {vlan_id}",
        f"interface {interface_name}",
        f"switchport trunk allowed vlan add {vlan_id}",
    ]

    try:
        with ConnectHandler(**device_params) as conn:
            output = conn.send_config_set(commands)

            try:
                conn.save_config()
            except Exception:
                pass

        return True, (
            f"VLAN {vlan_id} was added to trunk interface {interface_name} "
            f"on device {device['device_name']} via SSH\n\n{output}"
        )

    except Exception as e:
        return False, f"SSH exception on {device['device_name']}: {str(e)}"
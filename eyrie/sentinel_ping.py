import os
import platform
import subprocess
import json
from datetime import datetime
from dotenv import load_dotenv

# Load the secret IPs from your .env file
load_dotenv()

# Map the Clan roles to the environment variables
CLAN_NODES = {
    "High_Keep": os.getenv("HIGH_CLOUD_IP"),
    "Stone_Sentinel": os.getenv("STONE_SENTINEL_IP"),
    "Mobile_Rookery": os.getenv("MOBILE_ROOKERY_IP"),
}


def ping_node(name, address):
    """Checks if a node is Awake (Online) or in Stone (Offline)."""
    if not address or address == "0.0.0.0":
        return "UNCONFIGURED ⚪"

    # Handle cross-platform ping flags
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", address]

    try:
        # We run the ping and hide the messy output
        output = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "AWAKE 🟢" if output.returncode == 0 else "IN STONE 🗿"
    except Exception:
        return "ERROR ⚠️"


def rooftop_check():
    print(f"\n--- [ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] ---")
    print("CASTLE WYVERN: ROOFTOP STATUS CHECK\n")

    status_report = {}
    for name, addr in CLAN_NODES.items():
        status = ping_node(name, addr)
        status_report[name] = status
        print(f"[{name.replace('_', ' ')}]: {status}")

    # Log the status for Goliath to see
    log_path = os.path.join("eyrie", "heartbeat.json")
    with open(log_path, "w") as f:
        json.dump(status_report, f, indent=4)

    print(f"\nStatus logged to {log_path}. The night is ours.")


if __name__ == "__main__":
    rooftop_check()

import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD
from logger import logger

def get_netwatch_id(host):
    try:
        response = requests.get(
            f"{MIKROTIK_REST_API_URL}/tool/netwatch",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
        )
        response.raise_for_status()
        netwatch_list = response.json()
        for netwatch in netwatch_list:
            if netwatch.get("host") == host:
                return netwatch.get(".id")
        return None
    except Exception as e:
        logger.error(f"Failed to get netwatch ID for host {host}: {e}")
        return None

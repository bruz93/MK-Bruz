import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD
from logger import logger

def get_route_id(address):
    try:
        logger.debug("Fetching IP address list...")
        response = requests.get(
            f"{MIKROTIK_REST_API_URL}/ip/address",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
        )
        response.raise_for_status()
        data = response.json()
        # Cari ID berdasarkan address
        for entry in data:
            if entry.get("address") == address:
                logger.info(f"Found ID {entry.get('.id')} for address {address}")
                return entry.get(".id")
        logger.warning(f"Address {address} not found.")
        return None
    except Exception as e:
        logger.error(f"Failed to fetch IP list: {e}")
        return None

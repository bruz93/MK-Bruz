import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD
from logger import logger

def change_dns_server(old_server, new_server):
    try:
        logger.debug(f"Attempting to set DNS server to {new_server}")
        
        # Kirim permintaan untuk mengganti server DNS
        response = requests.patch(
            f"{MIKROTIK_REST_API_URL}/ip/dns/{old_server}",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"servers": [new_server]}
        )
        response.raise_for_status()

        logger.info(f"DNS berhasil diganti menjadi {new_server}.")
        return f"DNS telah berhasil diganti menjadi {new_server}."
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error saat mengganti DNS: {e}")
        return f"Kesalahan jaringan saat mengganti DNS. Error: {e}"
    except Exception as e:
        logger.error(f"Error tidak terduga saat mengganti DNS: {e}")
        return f"Gagal mengganti server DNS. Error: {e}"

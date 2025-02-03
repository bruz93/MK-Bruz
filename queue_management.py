import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD
from logger import logger
from queue_list import get_queue_list

def disable_queue(queue_name):
    try:
        logger.debug(f"Attempting to disable queue {queue_name}")
        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/queue/simple/{queue_name}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": "yes"}
        )
        response.raise_for_status()
        logger.info(f"Queue {queue_name} has been disabled.")
        return f"Queue {queue_name} telah di-disable."
    except Exception as e:
        logger.error(f"Failed to disable Queue {queue_name}: {e}")
        return f"Gagal men-disable Queue {queue_name}. Error: {e}"
    
def enable_queue(queue_name):
    try:
        logger.debug(f"Attempting to enable Queue {queue_name}")
        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/queue/simple/{queue_name}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": "no"}
        )
        response.raise_for_status()
        logger.info(f"Queue {queue_name} has been enabled.")
        return f"Queue {queue_name} telah di-enable."
    except Exception as e:
        logger.error(f"Failed to enable Queue {queue_name}: {e}")
        return f"Gagal men-enable Queue {queue_name}. Error: {e}"
    
def change_queue_limit(queue_name, queue_limit):
    try:
        logger.debug(f"Attempting to change Queue limit from {queue_name} to {queue_limit}")
        queue_list = get_queue_list()
        if not any(queue['name'] == queue_name for queue in queue_list):
            return f"Queue {queue_name} tidak ditemukan."

        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/queue/simple/{queue_name}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"max-limit": queue_limit}
        )
        response.raise_for_status()
        logger.info(f"Queue {queue_name} has been limit to {queue_limit}.")
        return f"Queue {queue_name} telah diganti limit menjadi {queue_limit}."
    except Exception as e:
        logger.error(f"Failed to change Queue limit from {queue_name} to {queue_limit}: {e}")
        return f"Gagal mengganti limit Queue {queue_name}. Error: {e}"
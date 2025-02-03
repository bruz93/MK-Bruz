import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD
from logger import logger
from route_list import get_route_list

def add_route(dst_address, gateway, distance, comment, routing_table="main", disabled=False):
    try:
        data = {
            "dst-address": dst_address,
            "gateway": gateway,
            "distance": distance,
            "comment": comment,
            "routing-table": routing_table,
            "disabled": disabled
        }
        logger.debug(f"Adding route user with data: {data}")
        response = requests.put(
            f"{MIKROTIK_REST_API_URL}/ip/route",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json=data
        )
        response.raise_for_status()
        logger.info(f"IP route {gateway} added successfully.")
        return f"IP address {gateway} berhasil ditambahkan."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return f"Gagal menambahkan IP address. HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Error adding IP address: {e}")
        return f"Gagal menambahkan IP address. Error: {e}"

def disable_route(route_id):
    try:
        logger.debug(f"Attempting to disable route {route_id}")
        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/ip/route/{route_id}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": "yes"}
        )
        response.raise_for_status()
        logger.info(f"route {route_id} has been disabled.")
        return f"route {route_id} telah di-disable."
    except Exception as e:
        logger.error(f"Failed to disable interface {route_id}: {e}")
        return f"Gagal men-disable interface {route_id}. Error: {e}"

def enable_route(route_id):
    try:
        logger.debug(f"Attempting to enable route {route_id}")
        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/ip/route/{route_id}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": "no"}
        )
        response.raise_for_status()
        logger.info(f"route {route_id} has been enable.")
        return f"route {route_id} telah di-enable."
    except Exception as e:
        logger.error(f"Failed to enable route {route_id}: {e}")
        return f"Gagal men-enable route {route_id}. Error: {e}"
    
def change_route_distance(old_distance, new_distance):
    try:
        logger.debug(f"Attempting to change route distance from {old_distance} to {new_distance}")
        route_list = get_route_list()
        if not any(route['.id'] == old_distance for route in route_list):
            return f"route {old_distance} tidak ditemukan."

        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/ip/route/{old_distance}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"distance": new_distance}
        )
        response.raise_for_status()
        logger.info(f"route {old_distance} has been change to {new_distance}.")
        return f"route {old_distance} telah diganti distance menjadi {new_distance}."
    except Exception as e:
        logger.error(f"Failed to change route distance from {old_distance} to {new_distance}: {e}")
        return f"Gagal mengganti distance route {old_distance}. Error: {e}"

def remove_route(route_id):
    try:
        if not route_id:
            return f"Route untuk id {route_id} tidak ditemukan."
        logger.debug(f"Attempting to remove route for {route_id}")
        response = requests.delete(
            f"{MIKROTIK_REST_API_URL}/ip/route/{route_id}",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
        )
        response.raise_for_status()
        logger.info(f"Route for {route_id} has been removed.")
        return f"route untuk {route_id} telah dihapus."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while removing route for {route_id}: {http_err}")
        return f"Gagal menghapus route untuk {route_id}. HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Failed to remove route for {route_id}: {e}")
        return f"Gagal menghapus route untuk {route_id}. Error: {e}"

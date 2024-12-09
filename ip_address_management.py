import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD
from logger import logger
from ip_address_list import get_ip_list
from ip_id import get_ip_id

def add_ip_address(address, interface, comment, disabled=False):
    try:
        data = {
            "address": address,
            "interface": interface,
            "comment": comment,
            "disabled": disabled
        }
        logger.debug(f"Adding address user with data: {data}")
        response = requests.put(
            f"{MIKROTIK_REST_API_URL}/ip/address",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json=data
        )
        response.raise_for_status()
        logger.info(f"IP address {address} added successfully.")
        return f"IP address {address} berhasil ditambahkan."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return f"Gagal menambahkan IP address. HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Error adding IP address: {e}")
        return f"Gagal menambahkan IP address. Error: {e}"

def disable_ip(address):
    try:
        # Dapatkan ID dari IP address
        ip_id = get_ip_id(address)
        if not ip_id:
            return f"IP address {address} tidak ditemukan."
        logger.debug(f"Attempting to disable IP {address} with ID {ip_id}")
        response = requests.patch(
            f"{MIKROTIK_REST_API_URL}/ip/address/{ip_id}",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": True} 
        )
        response.raise_for_status()
        logger.info(f"IP {address} has been disabled.")
        return f"IP {address} telah di-disable."
    except Exception as e:
        logger.error(f"Failed to disable IP {address}: {e}")
        return f"Gagal men-disable IP {address}. Error: {e}"

def enable_ip(address):
    try:
        ip_id = get_ip_id(address)
        if not ip_id:
            return f"IP address {address} tidak ditemukan."
        logger.debug(f"Attempting to enable IP {address} with ID {ip_id}")
        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/ip/address/{ip_id}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": "no"}
        )
        response.raise_for_status()
        logger.info(f"IP {address} has been enabled.")
        return f"IP {address} telah di-enable."
    except Exception as e:
        logger.error(f"Failed to enable ip {address}: {e}")
        return f"Gagal men-enable ip {address}. Error: {e}"

def change_ip_interface(address, new_interface):
    try:
        # Dapatkan ID berdasarkan IP address
        ip_id = get_ip_id(address)
        if not ip_id:
            return f"IP address {address} tidak ditemukan."
        logger.debug(f"Attempting to change interface for IP {address} to {new_interface}")
        # Kirim PATCH request untuk mengganti interface
        response = requests.patch(
            f"{MIKROTIK_REST_API_URL}/ip/address/{ip_id}",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"interface": new_interface}
        )
        response.raise_for_status()
        logger.info(f"Interface for IP {address} has been changed to {new_interface}.")
        return f"Interface untuk IP {address} berhasil diganti menjadi {new_interface}."
    except Exception as e:
        logger.error(f"Failed to change interface for IP {address} to {new_interface}: {e}")
        return f"Gagal mengganti interface untuk IP {address}. Error: {e}"

def remove_ip(address):
    try:
        # Dapatkan ID berdasarkan IP address
        ip_id = get_ip_id(address)
        if not ip_id:
            return f"IP address {address} tidak ditemukan."
        logger.debug(f"Attempting to remove ip {address}")
        # Pastikan ip ada sebelum dihapus
        ip_list = get_ip_list()
        if not any(ip['address'] == address for ip in ip_list):
            return f"IP {address} tidak ditemukan."
        # Mengirim request untuk menghapus ip
        response = requests.delete(
            f'{MIKROTIK_REST_API_URL}/ip/address/{ip_id}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
        )
        response.raise_for_status()
        logger.info(f"IP {address} has been removed.")
        return f"IP {address} telah dihapus."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while removing ip {address}: {http_err}")
        return f"Gagal menghapus ip {address}. HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Failed to remove ip {address}: {e}")
        return f"Gagal menghapus ip {address}. Error: {e}"

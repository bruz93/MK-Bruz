import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD
from logger import logger
from pppoe_list import get_pppoe_list

def add_pppoe_user(name, user, interface, service_name, password, profile, disabled=False):
    try:
        data = {
            "name": name,
            "user": user,
            "interface": interface,
            "service-name": service_name,
            "password": password,
            "profile": profile,
            "disabled": disabled
        }
        logger.debug(f"Adding PPPoE user with data: {data}")
        response = requests.put(
            f"{MIKROTIK_REST_API_URL}/interface/pppoe-client",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json=data
        )
        response.raise_for_status()
        logger.info(f"PPPoE user {user} added successfully.")
        return f"User PPPoE {user} berhasil ditambahkan."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return f"Gagal menambahkan PPPoE user. HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Error adding PPPoE user: {e}")
        return f"Gagal menambahkan PPPoE user. Error: {e}"

def disable_pppoe(interface_name):
    try:
        logger.debug(f"Attempting to disable pppoe {interface_name}")
        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/interface/pppoe-client/{interface_name}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": "yes"}
        )
        response.raise_for_status()
        logger.info(f"PPPOE {interface_name} has been disabled.")
        return f"PPPOE {interface_name} telah di-disable."
    except Exception as e:
        logger.error(f"Failed to disable pppoe {interface_name}: {e}")
        return f"Gagal men-disable pppoe {interface_name}. Error: {e}"

def enable_pppoe(interface_name):
    try:
        logger.debug(f"Attempting to enable pppoe {interface_name}")
        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/interface/pppoe-client/{interface_name}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": "no"}
        )
        response.raise_for_status()
        logger.info(f"PPPOE {interface_name} has been enabled.")
        return f"PPPOE {interface_name} telah di-enable."
    except Exception as e:
        logger.error(f"Failed to enable pppoe {interface_name}: {e}")
        return f"Gagal men-enable pppoe {interface_name}. Error: {e}"

def change_pppoe_name(old_name, new_name):
    try:
        logger.debug(f"Attempting to change pppoe name from {old_name} to {new_name}")
        # Cek apakah interface dengan nama lama ada
        pppoe_list = get_pppoe_list()
        if not any(interface['name'] == old_name for interface in pppoe_list):
            return f"Interface {old_name} tidak ditemukan."

        response = requests.patch(
            f'{MIKROTIK_REST_API_URL}/interface/pppoe-client/{old_name}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"name": new_name}
        )
        response.raise_for_status()
        logger.info(f"PPPOE {old_name} has been renamed to {new_name}.")
        return f"PPPOE {old_name} telah diganti namanya menjadi {new_name}."
    except Exception as e:
        logger.error(f"Failed to change pppoe name from {old_name} to {new_name}: {e}")
        return f"Gagal mengganti nama pppoe {old_name}. Error: {e}"

def remove_pppoe(interface_name):
    try:
        logger.debug(f"Attempting to remove pppoe {interface_name}")
        # Pastikan interface ada sebelum dihapus
        pppoe_list = get_pppoe_list()
        if not any(interface['name'] == interface_name for interface in pppoe_list):
            return f"Interface {interface_name} tidak ditemukan."
        # Mengirim request untuk menghapus interface
        response = requests.delete(
            f'{MIKROTIK_REST_API_URL}/interface/pppoe-client/{interface_name}',
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
        )
        response.raise_for_status()
        logger.info(f"PPPOE {interface_name} has been removed.")
        return f"PPPOE {interface_name} telah dihapus."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while removing pppoe {interface_name}: {http_err}")
        return f"Gagal menghapus pppoe {interface_name}. HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Failed to remove pppoe {interface_name}: {e}")
        return f"Gagal menghapus pppoe {interface_name}. Error: {e}"

import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD
from logger import logger
from netwatch_list import get_netwatch_list
from netwatch_id import get_netwatch_id


def add_netwatch(host, comment, interval="10s", up_script=None, down_script=None, disabled=False):
    if not host or not isinstance(host, str):
        return "Host harus berupa string yang valid."
    if not comment or not isinstance(comment, str):
        return "Comment harus berupa string yang valid."
    # Default scripts jika tidak diberikan
    up_script = up_script or (
        ":local hh $host\r\n"
        ":local bot \"7654165615:AAH1OkCz3owUyaI1AevHn04npneAmOg68fo\"\r\n"
        ":local chat \"225707008\"\r\n"
        ":local datetime \"Tanggal: $[/system clock get date] %0A Jam: $[/system clock get time]\"\r\n"
        ":local com [/tool netwatch get value-name=comment [find host=$hh] comment];\r\n"
        "/tool fetch url=\"https://api.telegram.org/bot$bot/sendmessage\\?chat_id=$chat&text=$datetime %0ARouter-WATUJIMBAR: $com $hh UP \\E2\\9C\\85 %0A%0A$com menyala wi \\F0\\9F\\94\\A5 \" keep-result=no"
    )
    down_script = down_script or (
        ":local hh $host\r\n"
        ":local bot \"7654165615:AAH1OkCz3owUyaI1AevHn04npneAmOg68fo\"\r\n"
        ":local chat \"225707008\"\r\n"
        ":local datetime \"Tanggal: $[/system clock get date] %0A Jam: $[/system clock get time]\"\r\n"
        ":local com [/tool netwatch get value-name=comment [find host=$hh] comment];\r\n"
        "/tool fetch url=\"https://api.telegram.org/bot$bot/sendmessage\\?chat_id=$chat&text=$datetime %0ARouter-WATUJIMBAR: $com $hh DOWN \\E2\\9D\\8C %0A%0A \\E2\\9A\\A0 $com sedang tidak baik baik saja, segera cek dan di koordinasikan ketua!!!!\" keep-result=no"
    )
    try:
        data = {
            "host": host,
            "comment": comment,
            "interval": interval,
            "up-script": up_script,
            "down-script": down_script,
            "disabled": disabled
        }
        logger.debug(f"Adding netwatch with data: {data}")
        response = requests.put(
            f"{MIKROTIK_REST_API_URL}/tool/netwatch",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json=data
        )
        response.raise_for_status()
        logger.info(f"netwatch host {host} added successfully.")
        return f"netwatch host {host} berhasil ditambahkan."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return f"Gagal menambahkan netwatch host . HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Error adding netwatch host : {e}")
        return f"Gagal menambahkan netwatch host . Error: {e}"

def disable_netwatch(host):
    try:
        # Dapatkan ID berdasarkan host
        netwatch_id = get_netwatch_id(host)
        if not netwatch_id:
            return f"Netwatch untuk host {host} tidak ditemukan."
        logger.debug(f"Attempting to disable netwatch for {host} with ID {netwatch_id}")
        response = requests.patch(
            f"{MIKROTIK_REST_API_URL}/tool/netwatch/{netwatch_id}",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": True}
        )
        response.raise_for_status()
        logger.info(f"Netwatch for {host} has been disabled.")
        return f"Netwatch untuk {host} telah dinonaktifkan."
    except Exception as e:
        logger.error(f"Failed to disable netwatch for {host}: {e}")
        return f"Gagal menonaktifkan Netwatch untuk {host}. Error: {e}"

def enable_netwatch(host):
    try:
        # Dapatkan ID berdasarkan host
        netwatch_id = get_netwatch_id(host)
        if not netwatch_id:
            return f"Netwatch untuk host {host} tidak ditemukan."
        logger.debug(f"Attempting to enable netwatch for {host} with ID {netwatch_id}")
        response = requests.patch(
            f"{MIKROTIK_REST_API_URL}/tool/netwatch/{netwatch_id}",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"disabled": "no"}  # Enable netwatch
        )
        response.raise_for_status()
        logger.info(f"Netwatch for {host} has been enabled.")
        return f"Netwatch untuk {host} telah diaktifkan."
    except Exception as e:
        logger.error(f"Failed to enable netwatch for {host}: {e}")
        return f"Gagal mengaktifkan Netwatch untuk {host}. Error: {e}"

def change_netwatch_host(old_host, new_host):
    try:
        # Dapatkan ID berdasarkan old_host
        netwatch_id = get_netwatch_id(old_host)
        if not netwatch_id:
            return f"Netwatch dengan host {old_host} tidak ditemukan."
        logger.debug(f"Attempting to change netwatch host from {old_host} to {new_host}")
        # Kirim request PATCH untuk mengubah host
        response = requests.patch(
            f"{MIKROTIK_REST_API_URL}/tool/netwatch/{netwatch_id}",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD),
            json={"host": new_host}
        )
        response.raise_for_status()
        logger.info(f"Netwatch host for {old_host} has been changed to {new_host}.")
        return f"Netwatch dengan host {old_host} telah diganti menjadi {new_host}."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while changing netwatch host: {http_err}")
        return f"Gagal mengganti host netwatch {old_host}. HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Failed to change netwatch host from {old_host} to {new_host}: {e}")
        return f"Gagal mengganti host netwatch {old_host}. Error: {e}"

def remove_netwatch(host):
    try:
        # Dapatkan ID berdasarkan host
        netwatch_id = get_netwatch_id(host)
        if not netwatch_id:
            return f"Netwatch untuk host {host} tidak ditemukan."
        logger.debug(f"Attempting to remove netwatch for {host}")
        response = requests.delete(
            f"{MIKROTIK_REST_API_URL}/tool/netwatch/{netwatch_id}",
            auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
        )
        response.raise_for_status()
        logger.info(f"Netwatch for {host} has been removed.")
        return f"Netwatch untuk {host} telah dihapus."
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while removing netwatch for {host}: {http_err}")
        return f"Gagal menghapus Netwatch untuk {host}. HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Failed to remove netwatch for {host}: {e}")
        return f"Gagal menghapus Netwatch untuk {host}. Error: {e}"
import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD

def get_ip_list():
    response = requests.get(
        f'{MIKROTIK_REST_API_URL}/ip/address',
        auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
    )
    response.raise_for_status()  # Akan memunculkan error jika status code bukan 200
    ips = response.json()

    # Tambahkan status enable/disable
    for ip in ips:
        ip['status'] = 'enabled' if ip.get('disabled') == 'false' else 'disabled'
        ip['invalid'] = 'valid' if ip.get('invalid') == 'false' else 'valid'
        ip['dynamic'] = 'Dynamic' if ip.get('dynamic') == 'true' else 'Static'
        ip['comment'] = ip.get('comment', '')
    
    return ips


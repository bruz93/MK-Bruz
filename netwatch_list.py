import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD

def get_netwatch_list():
    response = requests.get(
        f'{MIKROTIK_REST_API_URL}/tool/netwatch',
        auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
    )
    response.raise_for_status()  # Akan memunculkan error jika status code bukan 200
    netwatchs = response.json()

    # Tambahkan ipv6 
    for netwatch in netwatchs:
        netwatch['disabled'] = 'enabled' if netwatch.get('disabled') == 'false' else 'disabled'
        netwatch['status'] = 'up' if netwatch.get('status') == 'up' else 'down'
    
    return netwatchs
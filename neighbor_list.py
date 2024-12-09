import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD

def get_neighbor_list():
    response = requests.get(
        f'{MIKROTIK_REST_API_URL}/ip/neighbor',
        auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
    )
    response.raise_for_status()  # Akan memunculkan error jika status code bukan 200
    neighbors = response.json()

    # Tambahkan ipv6 
    for neighbor in neighbors:
        neighbor['ipv6'] = 'ipv6' if neighbor.get('ipv6') == 'true' else 'NoIpv6'
    
    return neighbors


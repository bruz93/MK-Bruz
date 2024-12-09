import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD

def get_pppoe_list():
    response = requests.get(
        f'{MIKROTIK_REST_API_URL}/interface/pppoe-client',
        auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
    )
    response.raise_for_status()  # Akan memunculkan error jika status code bukan 200
    interfaces = response.json()

    # Tambahkan status enable/disable
    for interface in interfaces:
        interface['status'] = 'enabled' if interface.get('disabled') == 'false' else 'disabled'
        interface['flags'] = 'Running' if interface.get('running') == 'true' else 'Not running'
        interface['dynamic'] = 'Dynamic' if interface.get('dynamic') == 'true' else 'Static'
        interface['comment'] = interface.get('comment', '')
    
    return interfaces


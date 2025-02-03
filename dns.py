import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD

def get_dns():
    response = requests.get(
        f'{MIKROTIK_REST_API_URL}/ip/dns',
        auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
    )
    response.raise_for_status()  
    dns = response.json()

    dns['allow-remote-requests'] = 'checked' if dns.get('allow-remote-requests') == 'true' else 'unchecked'
    dns['dynamic-servers'] = dns.get('dynamic-servers', '')
    
    return dns

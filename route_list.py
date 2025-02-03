import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD

def get_route_list():
    response = requests.get(
        f'{MIKROTIK_REST_API_URL}/ip/route',
        auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
    )
    response.raise_for_status()  
    routes = response.json()

    # Tambahkan status enable/disable
    for route in routes:
        route['status'] = 'disabled' if route.get('disabled') == 'true' else 'Enabled'
        route['inactive'] = 'active' if route.get('inactive') == 'false' else 'active'
        route['connect'] = 'disconnect' if route.get('connect') == 'false' else 'connect'
        route['dynamic'] = 'Dynamic' if route.get('dynamic') == 'true' else 'Static'
        route['ecmp'] = 'ecmp' if route.get('ecmp') == 'true' else 'noecmp'
        route['vpn'] = 'vpn' if route.get('vpn') == 'true' else 'novpn'
        route['hw-offloaded'] = 'hw-offloaded' if route.get('hw-offloaded') == 'true' else 'nohw-offloaded'
        route['suppress-hw-offload'] = 'suppress-hw-offload' if route.get('suppress-hw-offload') == 'true' else 'nosuppress-hw-offload'
        route['comment'] = route.get('comment', '')
        route['local-address'] = route.get('local-address', '')
        route['scope'] = route.get('scope', '')
        route['target-scope'] = route.get('target-scope', '')
        route['vrf-interface'] = route.get('vrf-interface', '')
        route['immediate-gw'] = route.get('immediate-gw', '')
    
    return routes
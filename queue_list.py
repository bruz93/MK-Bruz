import requests
from config import MIKROTIK_REST_API_URL, MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD

def get_queue_list():
    response = requests.get(
        f'{MIKROTIK_REST_API_URL}/queue/simple',
        auth=(MIKROTIK_REST_API_USER, MIKROTIK_REST_API_PASSWORD)
    )
    response.raise_for_status()  
    queues = response.json()
    # Tambahkan status enable/disable
    for queue in queues:
        queue['status'] = 'disabled' if queue.get('disabled') == 'true' else 'Enabled'
        queue['dynamic'] = 'Dynamic' if queue.get('dynamic') == 'true' else 'Static'
        queue['comment'] = queue.get('comment', '')
    
    return queues
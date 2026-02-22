import base64

def normalize_item_for_response(item):
    response_item = item.copy()
    if 'image' in response_item and isinstance(response_item['image'], bytes):
        response_item['image'] = base64.b64encode(response_item['image']).decode('utf-8')
    if 'lotNum' in response_item:
        response_item['lotNum'] = int(response_item['lotNum'])
    if 'timestamp' in response_item:
        response_item['timestamp'] = int(response_item['timestamp'])
    if 'status' in response_item:
        response_item['status'] = int(response_item['status'])
    return response_item

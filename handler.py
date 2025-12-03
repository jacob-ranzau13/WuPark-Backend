import os
import json
import boto3
import base64
import time
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')
table = dynamodb.Table(table_name)

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  
        },
        "body": json.dumps(body)
    }

def wupark_images(event, context):
    http_method = event.get('httpMethod')
    path_params = event.get('pathParameters') or {}
    body = event.get('body')

    try:
        if http_method == 'GET':
            lot_id = path_params.get('lotId')
            if lot_id:
                current_time = int(time.time())
                one_minute_ago = current_time - 60
                
                query_response = table.query(
                    KeyConditionExpression=Key('LotID').eq(int(lot_id)) & Key('Timestamp').gte(one_minute_ago)
                )
                items = query_response.get('Items', [])
                
                for item in items:
                    if 'Payload' in item and isinstance(item['Payload'], bytes):
                        item['Payload'] = base64.b64encode(item['Payload']).decode('utf-8')
                    item['LotID'] = int(item['LotID'])
                    item['Timestamp'] = int(item['Timestamp'])
                    item['Status'] = int(item['Status'])
                
                return response(200, items)
            else:
                current_time = int(time.time())
                one_minute_ago = current_time - 60
                
                scan_response = table.scan(
                    FilterExpression=Key('Timestamp').gte(one_minute_ago)
                )
                items = scan_response.get('Items', [])
                
               
                for item in items:
                    if 'Payload' in item and isinstance(item['Payload'], bytes):
                        item['Payload'] = base64.b64encode(item['Payload']).decode('utf-8')
                    item['LotID'] = int(item['LotID'])
                    item['Timestamp'] = int(item['Timestamp'])
                    item['Status'] = int(item['Status'])
                
                return response(200, items)

        elif http_method == 'POST':
            if not body:
                return response(400, {"message": "Missing request body"})

            data = json.loads(body)
            
            
            if 'LotID' not in data:
                return response(400, {"message": "LotID is required"})
            
            item = {
                'LotID': int(data['LotID']),
                'Timestamp': int(data.get('Timestamp', time.time())),
                'Status': int(data.get('Status', 0)),
            }
            
            if 'Payload' in data:
                
                if isinstance(data['Payload'], str):
                    item['Payload'] = base64.b64decode(data['Payload'])
                else:
                    item['Payload'] = data['Payload']

            table.put_item(Item=item)
            
            response_item = item.copy()
            if 'Payload' in response_item and isinstance(response_item['Payload'], bytes):
                response_item['Payload'] = base64.b64encode(response_item['Payload']).decode('utf-8')
            
            return response(201, response_item)

        else:
            return response(405, {"message": f"Method {http_method} not allowed"})

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {"message": "Internal server error", "error": str(e)})
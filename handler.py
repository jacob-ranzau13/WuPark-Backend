import os
import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key

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

def wupark_items(event, context):
    http_method = event.get('httpMethod')
    path_params = event.get('pathParameters') or {}
    body = event.get('body')

    try:
        if http_method == 'GET':
            item_id = path_params.get('id')
            if item_id:
                response_item = table.get_item(Key={'id': item_id})
                item = response_item.get('Item')
                if not item:
                    return response(404, {"message": f"Item with id {item_id} not found"})
                return response(200, item)
            else:
                scan_response = table.scan()
                items = scan_response.get('Items', [])
                return response(200, items)

        elif http_method == 'POST':
            if not body:
                return response(400, {"message": "Missing request body"})

            data = json.loads(body)
           
            item_id = str(uuid.uuid4())
            item = {"id": item_id}
            item.update(data)

            table.put_item(Item=item)
            return response(201, item)

        else:
            return response(405, {"message": f"Method {http_method} not allowed"})

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {"message": "Internal server error", "error": str(e)})
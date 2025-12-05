import os
import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')
table = dynamodb.Table(table_name)

def decimal_to_native(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    return obj

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(decimal_to_native(body))
    }

def parking_availability(event, context):
    """
    Handle parking availability data with schema:
    {
      "lotNum": number,
      "timestamp": number,
      "availability": {
        "[stall_id]": {
          "occupied": boolean
        }
      }
    }
    """
    http_method = event.get('httpMethod')
    path_params = event.get('pathParameters') or {}
    query_params = event.get('queryStringParameters') or {}
    body = event.get('body')

    try:
        if http_method == 'GET':
            lot_num = path_params.get('lotNum')
            
            
            if not lot_num:
                scan_response = table.scan(
                    Limit=1000  
                )
                items = scan_response.get('Items', [])
                
                if not items:
                    return response(200, {
                        "message": "No parking data found",
                        "data": None
                    })
                
                most_recent = max(items, key=lambda x: x.get('timestamp', 0))
                
                return response(200, {
                    "message": "Most recent parking availability",
                    "data": most_recent
                })
            
            try:
                lot_num = int(lot_num)
            except ValueError:
                return response(400, {"message": "lotNum must be a number"})
            
            query_kwargs = {
                'KeyConditionExpression': Key('lotNum').eq(lot_num),
                'Limit': 1,
                'ScanIndexForward': False  
            }
            
            query_response = table.query(**query_kwargs)
            items = query_response.get('Items', [])
            
            if not items:
                return response(200, {
                    "message": f"No parking data found for lot {lot_num}",
                    "data": None
                })
            
            return response(200, {
                "message": f"Most recent parking availability for lot {lot_num}",
                "data": items[0]
            })

        elif http_method == 'POST':
            if not body:
                return response(400, {"message": "Missing request body"})

            data = json.loads(body)
            
            if 'lotNum' not in data:
                return response(400, {"message": "lotNum is required"})
            if 'timestamp' not in data:
                return response(400, {"message": "timestamp is required"})
            if 'availability' not in data:
                return response(400, {"message": "availability is required"})
            
            if not isinstance(data['lotNum'], int):
                return response(400, {"message": "lotNum must be a number"})
            if not isinstance(data['timestamp'], int):
                return response(400, {"message": "timestamp must be a number"})
            if not isinstance(data['availability'], dict):
                return response(400, {"message": "availability must be an object"})
         
            for stall_id, stall_data in data['availability'].items():
                if not isinstance(stall_data, dict) or 'occupied' not in stall_data:
                    return response(400, {"message": f"Invalid structure for stall {stall_id}. Expected {{\"occupied\": boolean}}"})
                if not isinstance(stall_data['occupied'], bool):
                    return response(400, {"message": f"occupied field for stall {stall_id} must be a boolean"})
            
            item = {
                'lotNum': data['lotNum'],
                'timestamp': data['timestamp'],
                'availability': data['availability']
            }
            
            table.put_item(Item=item)
            
            return response(201, {
                "message": "Parking availability recorded successfully",
                "data": item
            })

        else:
            return response(405, {"message": f"Method {http_method} not allowed"})

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {"message": "Internal server error", "error": str(e)})
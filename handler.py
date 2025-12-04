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
                return response(400, {"message": "lotNum is required"})
            
            try:
                lot_num = int(lot_num)
            except ValueError:
                return response(400, {"message": "lotNum must be a number"})
            
            
            start_time = query_params.get('startTime')
            end_time = query_params.get('endTime')
            limit = query_params.get('limit', '100')
            
            try:
                limit = int(limit)
            except ValueError:
                limit = 100
            
            # Build query
            query_kwargs = {
                'KeyConditionExpression': Key('lotNum').eq(lot_num),
                'Limit': limit,
                'ScanIndexForward': False  
            }
        
            if start_time and end_time:
                try:
                    start_time = int(start_time)
                    end_time = int(end_time)
                    query_kwargs['KeyConditionExpression'] = Key('lotNum').eq(lot_num) & Key('timestamp').between(start_time, end_time)
                except ValueError:
                    return response(400, {"message": "startTime and endTime must be numbers"})
            elif start_time:
                try:
                    start_time = int(start_time)
                    query_kwargs['KeyConditionExpression'] = Key('lotNum').eq(lot_num) & Key('timestamp').gte(start_time)
                except ValueError:
                    return response(400, {"message": "startTime must be a number"})
            elif end_time:
                try:
                    end_time = int(end_time)
                    query_kwargs['KeyConditionExpression'] = Key('lotNum').eq(lot_num) & Key('timestamp').lte(end_time)
                except ValueError:
                    return response(400, {"message": "endTime must be a number"})
            
            query_response = table.query(**query_kwargs)
            items = query_response.get('Items', [])
            
            return response(200, {
                "lotNum": lot_num,
                "count": len(items),
                "items": items
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
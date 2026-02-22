import os
import json
import boto3
from decimal import Decimal
from get.get_handler import GetParkingAvailabilityHandler
from post.post_validation import PostParkingAvailabilityValidator
from post.post_storage import PostParkingAvailabilityRepository

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')
table = dynamodb.Table(table_name)

def json_default(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body, default=json_default)
    }

def parking_availability(event, context):
    http_method = event.get('httpMethod')
    path_params = event.get('pathParameters') or {}
    body = event.get('body')

    try:
        if http_method == 'GET':
            get_handler = GetParkingAvailabilityHandler(table)
            status_code, body = get_handler.handle(path_params)
            return response(status_code, body)

        if http_method == 'POST':
            validator = PostParkingAvailabilityValidator()
            item = validator.validate(body)
            repository = PostParkingAvailabilityRepository(table)
            repository.store(item)
            return response(201, {
                "message": "Parking availability recorded successfully",
                "data": item,
            })

        else:
            return response(405, {"message": f"Method {http_method} not allowed"})

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {"message": "Internal server error", "error": str(e)})
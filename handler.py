import os
import json
import boto3
from post.post_validation import PostRequestValidator
from post.post_storage import PostItemRepository
from post.response_formatting import normalize_item_for_response

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

def handler(event, context):
    http_method = event.get('httpMethod')
    body = event.get('body')

    try:
        if http_method == 'POST':
            validator = PostRequestValidator()
            item = validator.validate(body)
            repository = PostItemRepository(table)
            repository.store(item)
            response_item = normalize_item_for_response(item)
            return response(201, response_item)

        return response(405, {"message": f"Method {http_method} not allowed"})

    except ValueError as exc:
        return response(400, {"message": str(exc)})
    except Exception as exc:
        print(f"Error: {str(exc)}")
        return response(500, {"message": "Internal server error", "error": str(exc)})

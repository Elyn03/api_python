import json
import os
from http import HTTPStatus
import boto3

def handler(event, context):

    print(event)
    
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'
    user_table_name = os.environ.get("STORAGE_USERS_NAME")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(user_table_name)

    table.put_item(
        Item = {
            "id": event["user_id"],
            "email": event["user_email"],
            "token": event["user_token"]
        }
    )

    print("user created")
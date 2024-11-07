import json
import os
from http import HTTPStatus
from functools import wraps
import boto3
import uuid
import hmac
import hashlib
from boto3.dynamodb.conditions import Key

# from utils.wrapper import exception_handler

def handler(event, context):

    print(event)

    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'
    user_table_name = os.environ.get("STORAGE_USERS_NAME")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(user_table_name)

    print("httpMethod")
    print(event.get("httpMethod"))
    
    # check if method POST
    if not event.get("httpMethod") == "POST":
        print("hello pas post")
        return {
            "body": "bad request",
            "statusCode": HTTPStatus.BAD_REQUEST
        }
        
    # check if body exist
    if not event.get("body"):
        return {
            "body": "email required",
            "statusCode": HTTPStatus.BAD_REQUEST
        }

    user_email = json.loads(event["body"]).get("email")
    # user_email = event["body"].get("email")

    # check if email exist
    if not user_email:
        return {
            "body": "email not provided",
            "statusCode": HTTPStatus.BAD_REQUEST
        }

    # get user_email in the table
    res = table.query(
        IndexName="emails",
        KeyConditionExpression=Key("email").eq(user_email)
    )

    # create user uuid and token
    user_id = str(uuid.uuid4())
    msg = user_id + user_email
    user_token = hmac.new(user_id.encode(), msg.encode(), hashlib.sha256).hexdigest()

    # check if user_email exist in the table
    if not res["Items"]:
        print("insert email")
        table.put_item(
            Item = {
                "id": user_id,
                "email": user_email,
                "token": user_token
            }
        )
    else:
        print("get email")
        user_token = res["Items"][0].get("token")

    return {
        "body": user_token,
        "statusCode": HTTPStatus.OK
    }

import json
import os
from http import HTTPStatus
import boto3
import uuid
import hmac
import hashlib
from boto3.dynamodb.conditions import Key

# from utils.wrapper import exception_handler

def handler(event, context):

    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'
    user_table_name = os.environ.get("STORAGE_USERS_NAME")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(user_table_name)

    lambda_client = boto3.client("lambda")
    creation_user = os.environ.get("FUNCTION_USERCREATION_NAME")

    user_email = None
    try:
        # check if method POST
        if not event.get("httpMethod") == "POST":
            raise CustomException("http_error")
        
        # check if body exist
        if not event.get("body"):
            raise CustomException("body_error")
        
        user_email = json.loads(event["body"]).get("email")

        # check if email exist
        if not user_email:
            raise CustomException("email_error")
    
    except CustomException as error:
        return error.get_message_error()

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
        payload = {
            "user_id": user_id,
            "user_email": user_email,
            "user_token": user_token,
        }
        
        response = lambda_client.invoke(
            FunctionName=creation_user,  # environment variable
            InvocationType="Event",  # synchronous call
            Payload=json.dumps(payload),
        )        
        response_payload = response.get("Payload").read()
        print("insert email", response_payload)

    else:
        user_token = res["Items"][0].get("token")
        print("get email")

    return {
        "body": user_token,
        "statusCode": HTTPStatus.OK
    }

class CustomException(Exception):
    def __init__(self, title):
        self.title = title

    def get_message_error(self):
        response = {}

        if self.title == "http_error":
            response["body"] = "bad request"
            response["statusCode"] = HTTPStatus.BAD_REQUEST
        
        if self.title == "body_error":
            response["body"] = "email required"
            response["statusCode"] = HTTPStatus.BAD_REQUEST
        
        if self.title == "email_error":
            response["body"] = "email not provided"
            response["statusCode"] = HTTPStatus.BAD_REQUEST

        return response

import json
import os
from requests import HTTPError
from http import HTTPStatus
from functools import wraps
import boto3
from boto3.dynamodb.conditions import Attr

# from utils.wrapper import exception_handler

def exception_handler(func):
    @wraps(func)
    def wrapper(event, context):
        print(event)
        response = {}
        try:
            if not event["httpMethod"] == "GET":
                raise CustomException("http_error")

            if not event["headers"].get("x-api-key"):
                raise CustomException("headers_error")

            res = func(event, context)
        
            if res:
                response["body"] = json.dumps(res)        
            response["statusCode"] = HTTPStatus.OK

        except CustomException as error:
            response = error.get_message_error()
            
        return response

    return wrapper


@exception_handler
def handler(event, context):

    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'
    user_table_name = os.environ.get("STORAGE_USERS_NAME")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(user_table_name)

    user_token = event["headers"]["x-api-key"]

    # res = table.get_item(
    #     Key = { "id": user_id }
    # )

    res = table.scan(
        FilterExpression = Attr("token").eq(user_token)
    )

    data = res["Items"]

    try :
        if not data:
            raise CustomException("user_error")
    except CustomException as error:
        return error.get_message_error()
        
    return data[0].get("email")

class CustomException(Exception):
    def __init__(self, title):
        self.title = title

    def get_message_error(self):
        response = {}

        if self.title == "http_error":
            response["body"] = "bad request"
            response["statusCode"] = HTTPStatus.BAD_REQUEST
        
        if self.title == "headers_error":
            response["body"] = "x-api-key not provided"
            response["statusCode"] = HTTPStatus.FORBIDDEN
        
        if self.title == "user_error":
            response = "missing user"

        return response

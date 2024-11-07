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
                raise PermissionError("bad request")

            if not event.get("headers"):
                raise PermissionError("x-api-key not provided")
            res = func(event, context)

            if res:
                response["body"] = json.dumps(res)        
            response["statusCode"] = HTTPStatus.OK

        except HTTPError as error:
            response["statusCode"] = error.response.status_code
        except PermissionError as error:
            response["body"] = str(error)
            response["statusCode"] = HTTPStatus.FORBIDDEN
        except Exception as error:
            response["body"] = str(error)
            response["statusCode"] = HTTPStatus.INTERNAL_SERVER_ERROR
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

    if not data:
        raise ValueError("User missing")
    
    return data[0].get("email")
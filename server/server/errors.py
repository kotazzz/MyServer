from sanic import json

FAIL = json({"message": "Failed", "status": 400}, status=400)
UNAUTH = json({"message": "Unauthorized", "status": 401}, status=401)
DENIED = json({"message": "Access denied", "status": 403}, status=403)
INVALID = json({"message": "Inalid", "status": 400}, status=400)


def create_error(message="Invalid", status=400, **additional):
    return json({"message": message, "status": status, **additional}, status=status)


def create_success(message="Successfull", status=200, **additional):
    return json({"message": message, "status": status, **additional}, status=status)

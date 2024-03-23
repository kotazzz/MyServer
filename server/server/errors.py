from sanic import json

FAIL = json({"message": "Failed", "status": 400}, status=400)
UNAUTH = json({"message": "Unauthorized", "status": 401}, status=401)
DENIED = json({"message": "Access denied", "status": 403}, status=403)
import json
import bcrypt

from functools import wraps

import jwt
from sanic import Blueprint, json as json_response, text
from sanic.request import Request

auth = Blueprint("auth", url_prefix="/auth")


class UserManager:
    """
    # Пример использования:
    >>> user_manager = UserManager('user_data.json')

    >>> user_manager.register('john_doe', 'secure_password')

    >>> user_manager.login('john_doe', 'secure_password')
    """

    def __init__(self, filename):
        self.filename = filename
        self.users = {}
        self.load()

    def register(self, username, password):
        if username in self.users:
            return {"err": "User already exists."}

        salt = self.gensalt()
        hashed_password = self.get_hash(password, salt)
        self.users[username] = {"password": hashed_password, "salt": salt}
        self.save()

        return {}

    def login(self, username, password):
        if username not in self.users:
            return {"err": "User not found."}

        hashed_password = self.users[username]["password"]
        salt = self.users[username]["salt"]
        input_hash = self.get_hash(password, salt)

        if input_hash == hashed_password:
            return {}
        else:
            return {"err": "Invalid password."}

    def gensalt(self):
        return bcrypt.gensalt().decode("utf-8")

    def get_hash(self, password, salt):
        password = password.encode("utf-8")
        salt = salt.encode("utf-8")
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode("utf-8")

    def save(self):
        with open(self.filename, "w") as file:
            json.dump(self.users, file)

    def load(self):
        try:
            with open(self.filename, "r") as file:
                self.users = json.load(file)
        except FileNotFoundError:
            self.users = {}


manager = UserManager("users.json")


@auth.post("/register")
async def do_register(request: Request):
    user, password = request.json["user"], request.json["password"]
    if not manager.register(user, password):
        manager.save()
        token = jwt.encode({"user": user}, request.app.config.SECRET)
        return text(token)
    return json_response({"err": "Failed"}, status=400)


@auth.post("/login")
async def do_login(request: Request):
    user, password = request.json["user"], request.json["password"]
    if not manager.login(user, password):
        token = jwt.encode({"user": user}, request.app.config.SECRET)
        return text(token)
    return json_response({"err": "Failed"}, status=400)


def check_token(request: Request) -> bool:
    if not request.token:
        return False
    try:
        # TODO: replace
        jwt.decode(request.token, request.app.config.SECRET, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True


def decode_token(request: Request):
    if not request.token:
        return False
    try:
        # TODO: replace
        return jwt.decode(
            request.token, request.app.config.SECRET, algorithms=["HS256"]
        )
    except jwt.exceptions.InvalidTokenError:
        return None


def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated = check_token(request)

            if is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text("You are unauthorized.", 401)

        return decorated_function

    return decorator(wrapped)

import re
from functools import wraps

import bcrypt
import jwt
from sanic import Blueprint, Sanic, text
from sanic.request import Request
from sanic.response import JSONResponse
from server.errors import FAIL, INVALID, create_error, create_success
from server.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

auth = Blueprint("auth", url_prefix="/auth")


class UserManager:
    async def register(self, user: str, password: str):
        session: AsyncSession
        async with Sanic.get_app().ctx.session() as session:
            stmt = select(User).where(User.username == user)
            existing_user = (await session.scalars(stmt)).first()
            if existing_user:
                return False
            hashed = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")
            new_user = User(username=user, password_hash=hashed)
            session.add(new_user)
            await session.commit()
            return True

    async def login(self, user: str, user_password: str) -> bool:
        session: AsyncSession
        async with Sanic.get_app().ctx.session() as session:
            stmt = select(User).where(User.username == user)
            db_user = (await session.scalars(stmt)).first()
            if not db_user or db_user.password_hash is None:
                return False

            return bcrypt.checkpw(
                user_password.encode("utf-8"),
                db_user.password_hash.encode("utf-8"),
            )

    async def get_token(self, user: str, password: str):
        if self.login(user, password):
            return jwt.encode({"user": user}, Sanic.get_app().config.SECRET)
        return None

    async def check_token(self, token):
        try:
            data = jwt.decode(
                token, Sanic.get_app().config.SECRET, algorithms=["HS256"]
            )
            user = data.get("user")
            if not user:
                return False
            async with auth.ctx.session() as session:
                stmt = select(User).where(User.username == user)
                db_user = (await session.scalars(stmt)).first()
                return bool(db_user)
        except jwt.exceptions.InvalidTokenError:
            return False


def decode_token(request: Request):
    if not request.cookies["token"]:
        return None
    try:
        return jwt.decode(
            request.cookies["token"], request.app.config.SECRET, algorithms=["HS256"]
        )
    except jwt.exceptions.InvalidTokenError:
        return None


def protected(check=lambda: True):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            data = decode_token(request)
            if data:
                # Выполнение пользовательской функции проверки
                if check():
                    response = await f(request, *args, **kwargs)
                    return response
                else:
                    return text("Access denied.", status=403)
            else:
                return text("You are unauthorized.", status=401)

        return decorated_function

    return decorator


manager = UserManager()


@auth.before_server_start
async def attach_db(app: Sanic, loop):
    app.ctx.manager = manager


def check_username(username):
    # Username must start with an underscore or letter, be 3-17 characters long, and can contain letters, digits, underscores, and dots
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_.]{2,16}$"
    return bool(re.match(pattern, username))


def check_password(password):
    # Password must be at least 8 characters long, no more than 48 characters, contain at least one digit, one uppercase and one lowercase letter
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,48}$"
    return bool(re.match(pattern, password))


def validate_form(
    request: Request,
) -> tuple[None, None, JSONResponse] | tuple[str, str, None]:
    if not request.json:
        return None, None, INVALID
    username: str = request.json.get("username")
    password: str = request.json.get("password")
    if not username or not password:
        return None, None, INVALID
    if not check_username(username):
        return (
            None,
            None,
            create_error(
                "Username must start with an underscore or letter, "
                "be 3-17 characters long, and can contain letters, "
                "digits, underscores, and dots"
            ),
        )
    if not check_password(password):
        return (
            None,
            None,
            create_error(
                "Password must be at least 8 characters long, no "
                "more than 48 characters, contain at least one digit, "
                "one uppercase and one lowercase letter"
            ),
        )
    return username, password, None


def create_token_response(token: str):

    response = create_success("Login successful")
    response.cookies["token"] = token
    response.cookies["token"]["httponly"] = True
    response.cookies["token"]["secure"] = True
    response.cookies["token"]["samesite"] = "Strict"
    return response


@auth.post("/register")
async def do_register(request: Request):
    user, password, error = validate_form(request)
    if error or not user or not password:
        return error
    if await manager.register(user, password):
        token = jwt.encode({"user": user}, request.app.config.SECRET)
        return create_token_response(token)
    return FAIL


@auth.post("/login")
async def do_login(request: Request):
    user, password, error = validate_form(request)
    if error or not user or not password:
        return error
    if await manager.login(user, password):
        token = jwt.encode({"user": user}, request.app.config.SECRET)
        return create_token_response(token)
    return FAIL


@protected()
@auth.post("/test")
async def do_test(request: Request):
    return create_success("Success")


@protected()
@auth.post("/logout")
async def do_logout(request: Request):
    return create_token_response("")

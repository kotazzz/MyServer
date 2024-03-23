import bcrypt

from functools import wraps

import jwt
from sanic import Blueprint, json, text, Sanic
from sanic.request import Request
from server.models import User
from server.errors import FAIL
from sqlalchemy.sql.expression import select
from sqlalchemy.ext.asyncio import AsyncSession

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


manager = UserManager()


@auth.before_server_start
async def attach_db(app: Sanic, loop):
    app.ctx.manager = manager


@auth.post("/register")
async def do_register(request: Request):
    user, password = request.json["user"], request.json["password"]
    if await manager.register(user, password):
        token = jwt.encode({"user": user}, request.app.config.SECRET)
        return text(token)
    return FAIL


@auth.post("/login")
async def do_login(request: Request):
    user, password = request.json["user"], request.json["password"]
    if await manager.login(user, password):
        token = jwt.encode({"user": user}, request.app.config.SECRET)
        return text(token)
    return FAIL


def decode_token(request: Request):
    if not request.token:
        return None
    try:
        return jwt.decode(
            request.token, request.app.config.SECRET, algorithms=["HS256"]
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

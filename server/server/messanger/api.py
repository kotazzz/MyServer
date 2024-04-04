import re
from functools import wraps

import bcrypt
import jwt
from sanic import Blueprint, Sanic, Websocket, text
from sanic.request import Request
from sanic.response import JSONResponse
from server.errors import FAIL, INVALID, create_error, create_success
from server.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from server.auth import protected

api = Blueprint("api", url_prefix="/messanger")


@api.post("/load")
@protected()
async def do_load(request: Request):
    # return create_token_response("")
    pass

@api.websocket("/feed")
@protected()
async def feed(request: Request, ws: Websocket):
    async for msg in ws:
        await ws.send(msg if msg else "NoData")

import os

from dotenv import load_dotenv
from sanic import Request, Sanic, Websocket, text
from sanic_cors import CORS  # type: ignore
from server.auth import auth, decode_token, protected
from server.models import Base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv(os.getenv("DOTENV_FILE"))


app = Sanic("AuthApp")
app.config.SECRET = os.getenv("SECRET")
CORS(app)


@app.before_server_start
async def attach_db(app: Sanic, loop):
    file = os.getenv("POSTGRES_PASSWORD_FILE")
    if not file:
        raise Exception("No postgre password set")
    db_password = open(file).read()
    DATABASE_URL = f"postgresql+asyncpg://postgres:{db_password}@postgres:5432/postgres"
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    app.ctx.engine = engine
    app.ctx.session = async_session


app.blueprint(auth)


@app.get("/secret")
@protected()
async def secret(request: Request):
    return text(f"To go fast, you must be fast. {decode_token(request)}")


@app.get("/test")
async def test(request: Request):
    return text("Hi!?")


@app.websocket("/feed")
async def feed(request: Request, ws: Websocket):
    async for msg in ws:
        await ws.send(msg if msg else "NoData")

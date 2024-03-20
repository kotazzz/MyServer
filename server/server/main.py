import os
from dotenv import load_dotenv
from sanic import Request, Sanic, text
from sanic_cors import CORS
from server.auth import protected, auth, decode_token
import asyncio
from sqlalchemy import Table, MetaData, Integer, Column, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv(os.getenv("DOTENV_FILE"))


Base = declarative_base()
db_password = open(os.getenv("POSTGRES_PASSWORD_FILE")).read()
DATABASE_URL = f"postgresql+asyncpg://postgres:{db_password}@postgres:5432/postgres"
engine = create_async_engine(DATABASE_URL, echo=True)
metadata: MetaData = Base.metadata


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    email = Column(String(255))


# async def main():
#     async with engine.begin() as conn:
#         await conn.run_sync(metadata.drop_all)
#
#     async with engine.begin() as conn:
#         await conn.run_sync(metadata.create_all)
#
#     async_session = async_sessionmaker(
#         engine, expire_on_commit=False, class_=AsyncSession
#     )
#
#     async with async_session() as session:
#         async with session.begin():
#             username, email = "John Doe", "johndoe@example.com"
#             new_user = User(username=username, email=email)
#
#             session.add(new_user)
#             # await session.flush()
#
#             users = await session.execute(select(User))
#             for user in users.scalars():
#                 print(user, user.username, user.email)
#             await session.commit()


app = Sanic("AuthApp")
app.config.SECRET = os.getenv("SECRET")


@app.before_server_start
async def attach_db(app: Sanic, loop):
    # app.ctx.db = Database()
    Base = declarative_base()
    db_password = open(os.getenv("POSTGRES_PASSWORD_FILE")).read()
    DATABASE_URL = f"postgresql+asyncpg://postgres:{db_password}@postgres:5432/postgres"
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    app.ctx.engine = engine
    app.ctx.async_session = async_session


app.blueprint(auth)
CORS(app)


@app.get("/secret")
@protected
async def secret(request: Request):
    return text(f"To go fast, you must be fast. {decode_token(request)}")


@app.get("/test")
async def test(request: Request):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        async with session.begin():
            username, email = "John Doe", "johndoe@example.com"
            new_user = User(username=username, email=email)
            session.add(new_user)
            # await session.flush()
            users = await session.execute(select(User))
            return text(users.scalars().all()[0].username)

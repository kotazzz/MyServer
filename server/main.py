import os
from dotenv import load_dotenv
from sanic import Request, Sanic, text
from sanic_cors import CORS

from server.auth import protected, auth, decode_token

load_dotenv()

app = Sanic("AuthApp")
app.config.SECRET = os.getenv("SECRET")
app.blueprint(auth)
CORS(app)

@app.get("/secret")
@protected
async def secret(request: Request):
    return text(f"To go fast, you must be fast. {decode_token(request)}")

@app.get('/test')
def test(request: Request):
    return text("Hi")
from sanic import Blueprint
from sanic import Request, Websocket


ws_bp = Blueprint('ws', url_prefix='/ws')

@ws_bp.websocket('/endpoint')
async def websocket_handler(request: Request, ws: Websocket):
    async for msg in ws:
        data = await ws.recv()
        print(f"Received: {data}")
        await ws.send(f"You sent: {data}")


import asyncio
import websockets

async def connect_and_send(ws_url, user, command):
    async with websockets.connect(ws_url) as websocket:
        print(f"{user} > {command}")
        await websocket.send(command)
        response = await websocket.recv()
        print(f"{user} < {response}")

async def main():
    ws_url = "ws://kotaz.ddnsfree.com:24551/ws/endpoint"  # Замените на фактический URL вебсокета
    commands = [
        ("p1", "connect"),
        ("p2", "connect"),
        ("p1", "send", "list"),
        ("p2", "send", "list"),
    ]

    # Создаем соединение для каждого пользователя
    user_connections: dict[str, ] = {}
    for u, c, *a in commands:
        if c == "connect":
            user_connections[u] = await websockets.connect(ws_url)    
            print(f"{u} + connected")
        elif c =="send":
            await user_connections[u].send(a[0])
            print(f"{u} > {a[0]}")
            response = await user_connections[u].recv()
            print(f"{u} < {response}")
        elif c == "close":
            await user_connections[u].close(a[0])
            print(f"{u} - disconnected")
            
        

if __name__ == "__main__":
    asyncio.run(main())
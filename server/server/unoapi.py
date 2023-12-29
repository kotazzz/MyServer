from __future__ import annotations
import random
import ujson
import shlex
from uuid import UUID
from sanic import Blueprint
from sanic import Request, Websocket


ws_bp = Blueprint('ws', url_prefix='/ws')

UNKNOWN = {'err': 'unknown'}
NO_LOBBY = {'err': 'no lobby'}
ERROR = {'err': 'something wrong'}

class Adapter:
    
    def send(self, request: Request, message):
        raise NotImplemented
    
    async def check(self, request: Request):
        return True
    
    async def command(self, request: Request, *args):
        command, *args = args
        for i in dir(self):
            command = getattr(self, i)
            print(command, args)
            if isinstance(i, Command) and i.name == command:
                print(i)
                if await self.check(request):
                    try:
                        return await command.run(request, *args)
                    except Exception as e:
                        self.send(request, ERROR)
        await self.send(request, UNKNOWN)

class Command:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

    def run(self, request, *args):
        return self.callback(request, *args)

def command(name):
    def decorator(callback):
        return Command(name, callback)
    return decorator

class Lobby(Adapter):
    def __init__(self, game: GameWrapper):
        self.players: list[Request] = []
        self.game = game
        self.running = False
        
    def send(self, request: Request, msg):
        self.game.send(request, msg)
        
    def connect(self, request: Request):
        self.players.append(request)
    
    def disconnect(self, request: Request):
        for id, player in enumerate(self.players):
            # TODO: Make more cleanup
            if player is request:
                del self.players[id]

class GameWrapper(Adapter):
    def __init__(self):
        self.sockets: dict[Request, Websocket] = {}
        self.connections: dict[UUID, str] = {}
        
        self.lobbies: list[Lobby] = []
        
    def connect(self, request: Request, ws: Websocket):
        self.connections[request.id] = f'Player #{random.randint(1111, 9999)}'
        self.sockets[request] = ws
    
    def disconnect(self, request: Request):
        if request.id in self.connections:
            del self.connections[request.id]
        if request in self.sockets:
            del self.sockets[request]
    
    async def send(self,request: Request, msg: dict):
        await self.sockets[request].send(ujson.dumps(msg))
    
    async def check(self, request: Request):
        return not self.get_lobby(request)
    
    @command('create')
    async def lobby_create(self, request: Request):
        l = Lobby(self)
        self.lobbies.append(l)
        l.connect(request)
        
    @command('connect')
    async def lobby_connect(self, request: Request, number: int):
        if len(self.lobbies) > number and not self.lobbies[number].running:
            self.lobbies[number].connect(request)
    
    @command('list')
    def lobby_list(self, request: Request):
        return {
            "lobbies": [
                {"name": self.connections[l.players[0].id],
                 "players": len(l.players), "playing": l.running}
                for l in self.lobbies
            ], "online": len(self.connections)
            }
    
    def get_lobby(self, request: Request):
        for lobby in self.lobbies:
            if request in lobby.players:
                return lobby
            
    @command('lobby')
    async def create_lobby(self, request: Request, *args: str):
        lobby = self.get_lobby(request)
        if lobby:
            return lobby.command(*args)
        self.send(request, NO_LOBBY)
    
    
    

game = GameWrapper()

@ws_bp.websocket('/endpoint')
async def websocket_handler(request: Request, ws: Websocket):
    game.connect(request, ws)
    
    try:
        async for msg in ws:
            args = shlex.split(msg)
            await game.command(request, *args)
    except Exception as e:
        raise e
        # game.disconnect(request)
from __future__ import annotations
import random
import ujson
import shlex
from uuid import UUID
from sanic import Blueprint
from sanic import Request, Websocket

from server.uno import COLOR, Card, Hand, Deck, single_card_check

ws_bp = Blueprint('ws', url_prefix='/ws')

SUCCESS = {"status": "ok"}
NO_ARGS = {"err": "no args"}
WRONG_TYPE = {"err": "wrong type"}
WRONG_COMMAND = {"err": "wrong command"}
IN_LOBBY = {"err": "in lobby"}
IN_GAME = {"err": "in game"}
UNKNOWN = {"err": "unknown"}
MORE_PLAYERS = {"err": "more players"}
NO_PERM = {"err": "no perm"}
NOT_YOUR_TURN = {"err": "not your turn"}
CANT_USE = {"err": "cant use"}

class Player:
    def __init__(self, request: Request, ws: Websocket) -> None:
        self.request = request
        self.ws = ws
        self.lobby: Lobby | None = None
        

        self.hand = Hand()
        
    async def send(self, msg: dict):
        await self.ws.send(ujson.dumps(msg))
    
    @property
    def json(self):
        return self.request.id.hex
    
    
    @property
    def name(self):
        return self.request.id.hex

class Lobby:
    def __init__(self, game: GameWrapper) -> None:
        self.connected: list[Player] = []
        self.playing = False

        self.deck = Deck()
        self.deck.shuffle()
        self.top: Card | None = None
        self.direction = 1
        self.current = 0
        self._color = "RED"
        
    @property
    def color(self):
        return self.top.color if self.top and self.top.color else self._color
                
    @property    
    def json(self):
        return {
            "name": self.connected[0].request.id.hex,
            "connected": len(self.connected),
            "playing": self.playing
        }
    
    def info(self, player: Player):
        return {
            "hand": player.hand.json,
            "other": {p.name: len(p.hand.cards) for p in self.connected if p is not player},
            "top": self.top.json,
            "remain": len(self.deck.deck)
        }
    
    def init_game(self):
        for p in self.connected:
            p.hand.cards = []
            for _ in range(6):
                p.hand.cards.append(self.deck.deal())
        self.deck = Deck()
        self.deck.shuffle()
        self.top: Card = self.deck.deal()
        
    async def process(self, player: Player, command: str, *args: str):
        if command == "info":
            return {
                "players": [player.json for player in self.connected],
                "status": self.playing
            } | (self.info(player) if self.playing else {} )
            
        if command == "start":
            if len(self.connected) < 2:
                return MORE_PLAYERS
            if self.playing:
                return IN_GAME
            if not self.connected[0] is not player:
                return NO_PERM
            self.playing = True
            self.init_game()
            await self.broadcast_info()
        
        if command == "drop":
            if player is not self.connected[self.current]:
                return NOT_YOUR_TURN
            
            if not player.hand.can_hit:
                player.hand.take(self.deck)
                if not player.hand.can_hit:
                    await self.process_turn()
                    return CANT_USE
                
                
            if not args:
                return NO_ARGS
            if not args[0].isnumeric():
                return WRONG_TYPE
            
            num = int(args[0])
            if not 0 <= num < len(player.hand.cards):
                return WRONG_COMMAND

            card = player.hand.cards[num]
            
            if card.rank in ("DRAW4", "WILD"):
                if len(args) != 2:
                    return WRONG_COMMAND
                if args[1] not in COLOR:
                    return WRONG_TYPE
                self._color = args[1]
            
            if single_card_check(self.top, card, self.color):
                self.top = card
                player.hand.cards.pop(num)    
                await self.process_turn()
                
            return SUCCESS
        return UNKNOWN
    
    async def process_turn(self):
        await self.broadcast_info()
        
        def get_player(index: int):
            index *= self.direction
            return self.connected[(self.current + index)%len(self.connected)]
        def update(index: int):
            index *= self.direction
            self.current += index
            self.current = self.current % len(self.connected)
            
        if self.top == "DRAW4":
            get_player(1).hand.take(self.deck, 4)
            
        elif self.top == "SKIP":
            update(2)
            
        elif self.top == "REVERSE":
            self.direction *= -1
            
        elif self.top == "DRAW2":
            get_player(1).hand.take(self.deck, 4)
            
        elif self.top == "WILD":
            pass
        
        await self.broadcast_info()
    
    async def broadcast(self, message: dict):
        for p in self.connected:
            await p.send(message)
            
    async def broadcast_info(self):
        for p in self.connected:
            await p.send(self.info(p))
            
            
                
class GameWrapper:
    def __init__(self):
        self.players: list[Player] = []
        self.lobbies: list[Lobby] = []
        
    def connect(self, request: Request, ws: Websocket):
        self.players.append(Player(request, ws))
    
    def disconnect(self, request: Request):
        for i, p in enumerate(self.players):
            if p.request is request:
                del self.players[i]
                return
    
    async def process(self, request: Request, command: str, *args: str):
        player = self[request]
        res = await self.process_command(player, command, *args)
        await player.send(res)
        
    async def process_command(self, player: Player, command: str, *args: str):
        # await self[request].send([request.id.hex, command, args])
        if player.lobby:
            return await player.lobby.process(player, command, *args)
            
        if command == "create":
            self.lobbies.append(Lobby(self))
            self.lobbies[-1].connected.append(player)
            player.lobby = self.lobbies[0]

            return SUCCESS
            
        if command == "connect":
            if not args:
                return NO_ARGS
            if not args[0].isnumeric():
                return WRONG_TYPE
            
            num = int(args[0])
            if not 0 <= num < len(self.lobbies):
                return WRONG_COMMAND
            if self.lobbies[num].playing:
                return IN_GAME
            
            self.lobbies[num].connected.append(player)
            await self.lobbies[num].broadcast({"new": player.json})
            player.lobby = self.lobbies[num]
            return SUCCESS
        
        if command == "list":
            return {
                "lobbies": [lobby.json for lobby in self.lobbies],
                "online": len(self.players)
            }
        
        return UNKNOWN
            
        
            
    
    def __getitem__(self, request: Request):
        for p in self.players:
            if p.request is request:
                return p
        
    

game = GameWrapper()

@ws_bp.websocket('/endpoint')
async def websocket_handler(request: Request, ws: Websocket):
    game.connect(request, ws)
    
    try:
        async for msg in ws:
            args = shlex.split(msg)
            await game.process(request, *args)
    except Exception as e:
        raise e
        # game.disconnect(request)
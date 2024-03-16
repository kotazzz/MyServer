from __future__ import annotations
import random


COLOR = ("RED", "GREEN", "BLUE", "YELLOW")
RANK = (
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "SKIP",
    "REVERSE",
    "DRAW2",
    "DRAW4",
    "WILD",
)
CTYPE = {
    "0": "number",
    "1": "number",
    "2": "number",
    "3": "number",
    "4": "number",
    "5": "number",
    "6": "number",
    "7": "number",
    "8": "number",
    "9": "number",
    "SKIP": "action",
    "REVERSE": "action",
    "DRAW2": "action",
    "DRAW4": "nocolor",
    "WILD": "nocolor",
}

def single_card_check(top_card: Card, card: Card, color: str) -> bool:
    top_color = top_card.color or color
    return card.color==top_color or top_card.rank==card.rank or card.cardtype=='action_nocolor'

class Card:
    def __init__(
        self, color, rank
    ):
        self.rank = rank
        self.cardtype = CTYPE[rank]
        self.color = None if CTYPE[rank] == 'nocolor' else color
    
    def usable(self, top: Card):
        return single_card_check(top, self)    
    
    def __repr__(self):
        return f"{self.color} {self.rank}" if self.color else self.rank
    
    @property
    def json(self):
        return self.__repr__()
    
    
class Deck:
    def __init__(self):
        self.deck = []
        self.fill()
    
    def fill(self):
        for c in COLOR:
            for r in RANK:
                if CTYPE[r] != 'nocolor':
                    self.deck.append(Card(c, r))
                self.deck.append(Card(c, r))
    
    def shuffle(self):
        random.shuffle(self.deck)
        
    def deal(self):
        
        card = self.deck.pop()
        if len(self.deck) == 0:
            self.fill()
            self.shuffle()
        return card
    
    def __repr__(self):
        return str(self.deck)



class Hand:
    def __init__(self):
        self.cards: list[Card] = []
    
    def take(self, deck: Deck, count=1):
        for i in range(count):
            self.cards.append(deck.deal())
    
    def use(self, place: int, top_card=None):
        if top_card and not self.cards[place].usable():
            return
        return self.cards.pop(place)
    
    @property
    def can_hit(self, hand: Hand, card: Card):
        return any([x.usable(card) for x in self.cards])

    @property
    def json(self):
        return [i.json for i in self.cards]


class Game:
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.players: list[Hand] = []
        self.direction = 1
        self.current = 0
        
    def add_player(self):
        self.players.append(Hand())
    
    def start(self):
        for hand in self.players:
            hand.take(self.deck, 6)
            
        self.current = random.randint(0, len(self.players))
    
    def get_cards(self, player: int):
        return self.players[player].json()
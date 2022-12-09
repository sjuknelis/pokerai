import random
from game import score_possible_hands

SUITS = ["clubs","diamonds","hearts","spades"]
CARD_NAMES = ["ace","2","3","4","5","6","7","8","9","10","jack","queen","king"]

class Card:
  def __init__(self,suit,index):
    self.suit = suit
    self.index = index
  
  def __repr__(self):
    return "(%s of %s)" % (CARD_NAMES[self.index],SUITS[self.suit])

  def __eq__(self,other):
    return self.suit == other.suit and self.index == other.index

class Deck:
  cards = []

  def __init__(self):
    self.reset()

  def reset(self):
    for suit in range(len(SUITS)):
      for index in range(len(CARD_NAMES)):
        self.cards.append(Card(suit,index))
    random.shuffle(self.cards)
  
  def pull_random(self,num):
    pulled = []
    for _ in range(num):
      pulled.append(self.cards.pop())
      if len(self.cards) == 0:
        self.reset()
    return pulled
  
  def pull_certain(self,cards):
    for card in cards:
      self.cards.remove(card)

def three_player_sim(hand,table_shown,bets):
  deck = Deck()
  deck.pull_certain(hand + table_shown)
  players = [
    hand,
    deck.pull_random(2),
    deck.pull_random(2)
  ]
  table = table_shown + deck.pull_random(5 - len(table_shown))
  scores = [score_possible_hands(player,table) for player in players]
   
  BET_FACTOR = 0.5
  scores = [score + bets[index] * len(table_shown) * BET_FACTOR for (index,score) in enumerate(scores)]

  return scores

SIM_COUNT = 1000
HAND = [Card(0,11),Card(0,12)]
TABLE = []
BETS = [0,0,1]
if __name__ == "__main__":
  totals = [0,0,0]
  win_rate = 0
  for _ in range(SIM_COUNT):
    sim = three_player_sim(HAND,TABLE,BETS)
    totals = [a + b for a,b in zip(totals,sim)]
    if max(sim) == sim[0]:
      win_rate += 1
  totals = [item / SIM_COUNT for item in totals]
  win_rate /= SIM_COUNT
  print(totals,win_rate)
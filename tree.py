from functools import cmp_to_key
import random

from matplotlib.table import Table
from better_prob import Card
from main import score_possible_hands

class SuitNode:
  def __init__(self,value,suits_seen,numbers_seen,parent):
    self.value = value
    self.suits_seen = suits_seen
    self.numbers_seen = numbers_seen
    self.parent = parent
  def get_children(self):
    results = []
    for i in range(13):
      odds = 4 - self.numbers_seen.count(i)
      results.append((NumberNode(i,self.suits_seen,self.numbers_seen + [i],self),odds))
    results.sort(key=cmp_to_key(lambda a,b: b[1] - a[1]))
    return results

class NumberNode:
  def __init__(self,value,suits_seen,numbers_seen,parent):
    self.value = value
    self.suits_seen = suits_seen
    self.numbers_seen = numbers_seen
    self.parent = parent
  def get_children(self):
    results = []
    for i in range(4):
      odds = 13 - self.suits_seen.count(i)
      results.append((SuitNode(i,self.suits_seen,self.numbers_seen + [i],self),odds))
    results.sort(key=cmp_to_key(lambda a,b: b[1] - a[1]))
    return results

def simulate(node,hand,table_shown):
  cards = []
  for _ in range(9 - len(table_shown)):
    number = node.value
    suit = node.parent.value
    cards.append(Card(suit,number))
    node = node.parent.parent
  table = table_shown + cards[:5 - len(table_shown)]
  players = [
    hand,
    cards[5 - len(table_shown):7 - len(table_shown)],
    cards[7 - len(table_shown):]
  ]
  scores = [score_possible_hands(player,table) for player in players]
  return scores

def select_random_child(node):
  children = node.get_children()
  total = sum([child[1] for child in children])
  print(total)
  value = random.randint(1,total)
  for (child,odds) in children:
    value -= odds
    if value <= 0:
      return child

def monte_carlo_from_node(node,hand,table_depth,table_shown,sim_count):
  wins = 0
  original_node = node
  for _i in range(sim_count):
    for _j in range(9 - table_depth):
      node = select_random_child(node)
      node = select_random_child(node)
    scores = simulate(node,hand,table_shown)
    print(scores)
    if scores[0] == max(scores):
      wins += 1
    node = original_node
  return wins / sim_count

node = NumberNode(0,[0,0,1,1,1],[12,11,12,11,10],None).get_children()[0][0].get_children()[0][0].get_children()[0][0].get_children()[0][0]
print(monte_carlo_from_node(node,[Card(0,12),Card(0,1)],3,[Card(1,12),Card(1,11),Card(1,10)],50))
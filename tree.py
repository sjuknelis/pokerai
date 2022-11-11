from functools import cmp_to_key
import random,math

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
      odds = 1
      for (suit,number) in zip(self.suits_seen,self.numbers_seen):
        if suit == self.value and number == i:
          odds = 0
          break
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
      results.append((SuitNode(i,self.suits_seen + [i],self.numbers_seen,self),odds))
    results.sort(key=cmp_to_key(lambda a,b: b[1] - a[1]))
    return results

def simulate(node):
  cards = []
  for (suit,number) in zip(node.suits_seen,node.numbers_seen):
    cards.append(Card(suit,number))
  table = cards[2:7]
  players = [
    cards[:2],
    cards[7:9],
    cards[9:]
  ]
  scores = [score_possible_hands(player,table) for player in players]
  return scores

def select_random_child(node):
  children = node.get_children()
  total = sum([child[1] for child in children])
  value = random.randint(1,total)
  for (child,odds) in children:
    value -= odds
    if value <= 0:
      return child

def monte_carlo_from_node(node,sim_count):
  wins = 0
  original_node = node
  for _i in range(sim_count):
    for _j in range(11 - len(node.suits_seen)):
      node = select_random_child(node)
      node = select_random_child(node)
    if len(node.numbers_seen) < 11:
      node = select_random_child(node)
    scores = simulate(node)
    if scores[0] == max(scores):
      wins += 1
    node = original_node
  return wins / sim_count

def dfs_list(node,max_count,max_depth):
  result = set()
  def dfs(node,depth):
    if depth >= max_depth:
      result.add(node)
      return
    for (child,odds) in node.get_children():
      if len(result) >= max_count:
        return
      if child not in result:
        dfs(child,depth + 1)
  dfs(node,0)
  return result

def bfs_list(node,max_count):
  result = set([node])
  queue = [node]
  while len(queue) > 0 and len(result) < max_count:
    chosen = queue.pop(0)
    for (child,odds) in node.get_children():
      if len(result) >= max_count:
        return result
      if child not in result:
        result.add(child)
        queue.append(child)
  return result

def djikstra_mod_list(node,max_count):
  found_nodes = []
  heap = Heap(node.get_children())
  while len(found_nodes) < max_count:
    (chosen_node,chosen_odds) = heap.pop()
    found_nodes.append(chosen_node)
    for (child_node,child_odds) in chosen_node.get_children():
      heap.insert((child_node,chosen_odds + child_odds))
  return found_nodes

class Heap:
  data = []
  def __init__(self,data):
    for item in data:
      self.insert(item)
  def push_up(self,index):
    parent_index = index
    while parent_index > 0:
      current_index = parent_index
      parent_index = math.floor((current_index - 1) / 2)
      if self.data[parent_index][1] < self.data[current_index][1]:
        old_parent = self.data[parent_index]
        self.data[parent_index] = self.data[current_index]
        self.data[current_index] = old_parent
      else:
        return
  def push_down(self,index):
    current_index = index
    depth = math.floor(math.log2(len(self.data))) + 1
    first_leaf = math.pow(2,depth - 1) - 1
    while current_index < first_leaf:
      child_a = self.data[current_index * 2 + 1]
      if current_index * 2 + 2 >= len(self.data):
        priority_child = child_a
        priority_child_index = current_index * 2 + 1
      else:
        child_b = self.data[current_index * 2 + 2]
        if child_a[1] > child_b[1]:
          priority_child = child_a
          priority_child_index = current_index * 2 + 1
        else:
          priority_child = child_b
          priority_child_index = current_index * 2 + 2
      if self.data[current_index][1] < priority_child[1]:
        old_current = self.data[current_index]
        self.data[current_index] = self.data[priority_child_index]
        self.data[priority_child_index] = old_current
      else:
        return
  def insert(self,item):
    self.data.append(item)
    self.push_up(len(self.data) - 1)
  def pop(self):
    if len(self.data) == 0:
      return None
    last_leaf = self.data.pop()
    if len(self.data) == 0:
      return last_leaf
    else:
      old_root = self.data[0]
      self.data[0] = last_leaf
      self.push_down(0)
      return old_root

node = NumberNode(0,[0,0,1],[8,9,12],None)
#print(monte_carlo_from_node(node,[Card(0,8),Card(0,9)],3,[Card(1,12)],500))
print(node)
found = bfs_list(node,20)
probs = []
for found_node in found:
  probs.append(monte_carlo_from_node(found_node,500))
probs.sort()
print(probs)
diffs = []
for i in range(len(probs) - 1):
  diffs.append(round(probs[i + 1] - probs[i],3))
print(diffs)

"""h = Heap([("a",2),("b",5),("c",1),("d",6)])
print(h.pop())
print(h.pop())
print(h.pop())
print(h.pop())"""
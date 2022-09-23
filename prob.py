import math

CARD_NAMES = ["ace","2","3","4","5","6","7","8","9","10","jack","queen","king"]

def get_combinations(n):
  out = []
  for a in range(len(CARD_NAMES)):
    for b in range(len(CARD_NAMES)):
      if n == 2:
        out.append([a,b])
        continue
      else:
        for c in range(len(CARD_NAMES)):
          out.append([a,b,c])
  return out

def invert_dict(original):
  out = {}
  for (key,value) in original.items():
    if value not in out:
      out[value] = [key]
    else:
      out[value].append(key)
  return out

def score_hand(hand):
  hand_indices = sorted(hand)
  index_count = {}
  for index in set(hand_indices):
    index_count[index] = hand_indices.count(index)
  inverted_index_count = invert_dict(index_count)
  index_count = list(index_count.values())

  is_straight = set([hand_indices[i + 1] - hand_indices[i] for i in range(4)]) == {1}

  hand_id = 0
  hand_addl = 0
  if is_straight:
    hand_id = 5 # straight
    hand_addl = max(hand_indices)
  else:
    unique_count = len(set(hand_indices))
    if unique_count == 2:
      if 4 in index_count:
        hand_id = 8 # four of a kind
        hand_addl = inverted_index_count[4][0]
      else:
        hand_id = 7 # full house
        hand_addl = inverted_index_count[3][0]
    elif unique_count == 3:
      if 3 in index_count:
        hand_id = 4 # three of a kind
        hand_addl = inverted_index_count[3][0]
      else:
        hand_id = 2 # two pair
        hand_addl = max(inverted_index_count[2]) * len(CARD_NAMES) + min(inverted_index_count[2])
    elif unique_count == 4:
      hand_id = 1 # pair
      hand_addl = inverted_index_count[2][0]
    else:
      hand_addl = max(hand_indices)

  return hand_id * len(CARD_NAMES) + hand_addl

def score_hands_for_player(player):
  scores = []
  for table in get_combinations(3):
    scores.append(score_hand(player + table))
  score_table = {}
  for score in scores:
    if score not in score_table:
      score_table[score] = 1
    else:
      score_table[score] += 1
  return score_table

def calc_overall_table():
  overall_table = {}
  for player in get_combinations(2):
    score_table = score_hands_for_player(player)
    for score in score_table:
      if score not in overall_table:
        overall_table[score] = score_table[score]
      else:
        overall_table[score] += score_table[score]
  return overall_table

def avg_from_table(table):
  total = 0
  for score in table:
    total += score * table[score]
  return total / sum(table.values())

def pprint_table(table):
  max_count = max(table.values())
  for score in range(0,8 * len(CARD_NAMES) + 12):
    if score in table:
      count = table[score]
    else:
      count = 1
    print("%d: %d    \t%s" % (score,count,"#" * math.ceil(count / max_count * 50)))

table = score_hands_for_player([3,4])
print(avg_from_table(table))
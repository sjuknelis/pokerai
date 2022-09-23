import pygame,random,sys,time

SUITS = ["clubs","diamonds","hearts","spades"]
CARD_NAMES = ["ace","2","3","4","5","6","7","8","9","10","jack","queen","king"]
IMAGE_RATIO = 726 / 500
SCREEN_SIZE = 600

card_images = []
for suit in SUITS:
  for card_name in CARD_NAMES:
    card_images.append(pygame.image.load("cards/" + card_name + "_of_" + suit + ".png"))
card_images.append(pygame.image.load("cards/hidden.png"))

class Card:
  hidden_cb = lambda self: False
  faded_cb = lambda self: False

  def __init__(self,suit,index):
    self.suit = suit
    self.index = index
  
  def __repr__(self):
    return "(%s of %s)" % (CARD_NAMES[self.index],SUITS[self.suit])

  def get_image(self):
    if not self.hidden_cb():
      base = card_images[self.suit * len(CARD_NAMES) + self.index]
    else:
      base = card_images[-1]
    
    if not self.faded_cb():
      return base
    else:
      faded = base.copy().convert_alpha()
      faded.fill((255,255,255,128),None,pygame.BLEND_RGBA_MULT)
      return faded

class Deck:
  cards = []

  def __init__(self):
    self.reset()

  def reset(self):
    for suit in range(len(SUITS)):
      for index in range(len(CARD_NAMES)):
        self.cards.append(Card(suit,index))
    random.shuffle(self.cards)
  
  def pull(self,num,hidden_cb,faded_cb):
    pulled = []
    for _ in range(num):
      pulled.append(self.cards.pop())
      pulled[-1].hidden_cb = hidden_cb
      pulled[-1].faded_cb = faded_cb
      if len(self.cards) == 0:
        self.reset()
    return pulled

def invert_dict(original):
  out = {}
  for (key,value) in original.items():
    if value not in out:
      out[value] = [key]
    else:
      out[value].append(key)
  return out

def score_hand(hand):
  hand_indices = sorted([card.index for card in hand])
  index_count = {}
  for index in set(hand_indices):
    index_count[index] = hand_indices.count(index)
  inverted_index_count = invert_dict(index_count)
  index_count = list(index_count.values())

  is_flush = len(set([card.suit for card in hand])) == 1
  is_straight = set([hand_indices[i + 1] - hand_indices[i] for i in range(4)]) == {1}
  is_royal = hand_indices == [0,10,11,12,13]
  if is_royal:
    is_straight = True

  hand_id = 0
  hand_addl = 0
  if is_flush:
    if is_royal:
      hand_id = 10 # royal flush
    elif is_straight:
      hand_id = 9 # straight flush
      hand_addl = max(hand_indices)
    else:
      hand_id = 6 # flush
      hand_addl = max(hand_indices)
  elif is_straight:
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

def score_possible_hands(player,table):
  hands = []
  for i in range(5):
    for j in range(i + 1,5):
      for k in range(j + 1,5):
        hands.append([table[i],table[j],table[k]] + player)
  for i in range(5):
    hands.append(table[:i] + table[i + 1:] + [player[0]])
    hands.append(table[:i] + table[i + 1:] + [player[1]])
  hands.append(table)

  max_score = 0
  for hand in hands:
    score = score_hand(hand)
    if score > max_score:
      max_score = score
  return max_score

class Game:
  def __init__(self):
    self.reset()

  def reset(self):
    self.deck = Deck()
    self.stage = 0
    self.player = 0
    self.folded = [False,False,False]
    self.winner = -1
    
    self.last_raise = 0
    self.pot_amount = 0
    self.round_bets = [0,0,0]
    self.now_betting = 0

    self.hands = [
      self.deck.pull(2,lambda: self.player != 0 and self.stage < 4,lambda: self.folded[0]),
      self.deck.pull(2,lambda: self.player != 1 and self.stage < 4,lambda: self.folded[1]),
      self.deck.pull(2,lambda: self.player != 2 and self.stage < 4,lambda: self.folded[2])
    ]
    self.table = (
      self.deck.pull(3,lambda: self.stage <= 0,lambda: False) +
      self.deck.pull(1,lambda: self.stage <= 1,lambda: False) +
      self.deck.pull(1,lambda: self.stage <= 2,lambda: False)
    )

  def next_player(self):
    self.player = (self.player + 1) % 3
    while self.folded[self.player]:
      self.player = (self.player + 1) % 3
    if self.player == self.last_raise:
      self.next_stage()
    else:
      self.now_betting = max(self.round_bets) - self.round_bets[self.player]

  def next_stage(self):
    self.stage += 1
    self.player = self.folded.index(False)
    self.last_raise = self.player
    self.round_bets = [0,0,0]
    self.now_betting = 0

    if self.stage == 4:
      max_score = 0
      max_player = 0
      for player in range(3):
        if not self.folded[player]:
          score = score_possible_hands(self.hands[player],self.table)
          if score > max_score:
            max_score = score
            max_player = player
      self.winner = max_player

  def keypress(self,key):
    if key == pygame.K_r:
      self.reset()
    elif self.stage == 4:
      return
    elif key == pygame.K_w:
      self.now_betting += 1
    elif key == pygame.K_s:
      self.now_betting -= 1
      if self.now_betting < max(self.round_bets) - self.round_bets[self.player]:
        self.now_betting = max(self.round_bets) - self.round_bets[self.player]
    elif key == pygame.K_b:
      self.pot_amount += self.now_betting
      old_max = max(self.round_bets)
      self.round_bets[self.player] += self.now_betting
      if self.round_bets[self.player] > old_max:
        self.last_raise = self.player
      
      self.next_player()
    elif key == pygame.K_f:
      self.folded[self.player] = True

      if self.folded.count(False) > 1:
        old_player = self.player
        self.next_player()
        if self.last_raise == old_player:
          self.last_raise = (self.last_raise + 1) % 3
      else:
        self.stage = 3
        self.next_stage()

game = Game()

def render(screen):
  def draw_card_list(cards,pos):
    for (index,card) in enumerate(cards):
      screen.blit(
        pygame.transform.scale(
          card.get_image(),
          (75,75 * IMAGE_RATIO)
        ),
        (pos[0] + 80 * index,pos[1])
      )

  screen.fill((51,101,77))
  draw_card_list(game.hands[0],(5,5))
  draw_card_list(game.hands[1],(SCREEN_SIZE - 80 * 2,SCREEN_SIZE / 2 - 75 * IMAGE_RATIO / 2))
  draw_card_list(game.hands[2],(5,SCREEN_SIZE - 75 * IMAGE_RATIO - 5))
  draw_card_list(game.table,(5,SCREEN_SIZE / 2 - 75 * IMAGE_RATIO / 2))

  GOLD = (255,215,0)
  if game.winner == 0:
    pygame.draw.circle(screen,GOLD,(25,30 + 75 * IMAGE_RATIO),20)
  elif game.winner == 1:
    pygame.draw.circle(screen,GOLD,(SCREEN_SIZE - 25,30 + SCREEN_SIZE / 2 + 75 * IMAGE_RATIO / 2),20)
  elif game.winner == 2:
    pygame.draw.circle(screen,GOLD,(25,SCREEN_SIZE - 30 - 75 * IMAGE_RATIO),20)

  font = pygame.font.Font(None,30)
  text_start = SCREEN_SIZE / 2 + 75 * IMAGE_RATIO * (3 / 4)
  text = [
    "Pot: $%d" % game.pot_amount
  ]
  if game.stage < 4:
    text += [
      "Current bet: $%d ($%d req.)" % (max(game.round_bets),max(game.round_bets) - game.round_bets[game.player]),
      "Now betting: $%d" % game.now_betting
    ]
  for (index,line) in enumerate(text):
    screen.blit(
      font.render(line,1,(255,255,255)),
      (5,text_start + 20 * index)
    )

def main():
  pygame.init()
  pygame.display.set_caption("Poker")
  screen = pygame.display.set_mode((SCREEN_SIZE,SCREEN_SIZE))

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()
      elif event.type == pygame.KEYDOWN:
        game.keypress(event.key)
    
    render(screen)
    pygame.display.update()
    time.sleep(1 / 30)

if __name__ == "__main__":
  main()
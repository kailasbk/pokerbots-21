import random, eval7, csv

VALUES = {'2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'}
SUITS = {'h', 'd', 's', 'c'}
NONE = str('0')

cton = {
	'2': 2,
	'3': 3,
	'4': 4,
	'5': 5,
	'6': 6,
	'7': 7,
	'8': 8,
	'9': 9,
	'T': 10,
	'J': 11,
	'Q': 12,
	'K': 13,
	'A': 14,
}

ntoc = {
	1: 'A',
	2: '2',
	3: '3',
	4: '4',
	5: '5',
	6: '6',
	7: '7',
	8: '8',
	9: '9',
	10: 'T',
	11: 'J',
	12: 'Q',
	13: 'K',
	14: 'A',
}

hole_strengths = {}

file = open('hole_strengths.csv', 'r')
reader = csv.DictReader(file)
for row in reader:
	hole_strengths[row['hole cards']] = row['strength']

def all_cards_excluding(excludes: list = []) -> list:
	"""
	Lists all cards not in `excludes`

	Args:
		excludes: a list of strings for cards not to include.

	Returns:
		A list of strings corresponding to all other cards in the deck.
	"""
	cards = []

	for value in VALUES:
		for suit in SUITS:
			card = value + suit
			if card not in excludes:
				cards.append(card)

	return cards

def sort_cards(cards: list) -> list:
	for i in range(len(cards)):
		k = i
		for j in range(i, len(cards)):
			if cton[cards[j][0]] < cton[cards[k][0]]:
				k = j

		temp = cards[i]
		cards[i] = cards[k]
		cards[k] = temp

	return cards

# assume sorted
def highest_pair(cards: list, exclude: str = NONE) -> str:
	highest = NONE

	for i in range(len(cards) - 1):
		if cards[i][0] != exclude and cards[i][0] == cards[i + 1][0]:
			highest = cards[i][0]

	return highest

# assume sorted
def highest_triple(cards: list, exclude: str = NONE) -> str:
	highest = NONE

	for i in range(len(cards) - 2):
		if cards[i][0] != exclude and cards[i][0] == cards[i + 2][0]:
			highest = cards[i][0]

	return highest

# assume sorted
def highest_quad(cards: list) -> str:
	highest = NONE

	for i in range(len(cards) - 3):
		if cards[i][0] == cards[i + 3][0]:
			highest = cards[i][0]

	return highest

# assume sorted
def highest_flush(cards: list) -> str:
	highest = NONE

	for suit in SUITS:
		count = 0
		potential = '2'
		for card in cards:
			if card[1] == suit:
				count += 1
				if cton[potential] < cton[card[0]]:
					potential = card[0]

		if count >= 5:
			highest = potential

	return highest

# assume sorted
def highest_straight(cards: list) -> str:
	highest = NONE

	for i in range(len(cards)):
		count = 0
		potential = NONE
		for j in range(i, len(cards) - 1):
			diff = cton[cards[j + 1][0]] - cton[cards[j][0]]
			if diff == 1:
				potential = cards[j + 1][0]
				count += 1
			elif diff != 0:
				break

		if (count >= 5):
			highest = potential

	return highest

# dont assume sorted
def best_hand(cards: list) -> str:
	if (len(cards) == 0):
		return ''
	
	sorted = sort_cards(cards)

	high_pair = highest_pair(sorted)
	low_pair = NONE
	high_triple = NONE
	if high_pair != NONE:
		high_quad = highest_quad(sorted)
		if high_quad != NONE:
			return 'Q' + high_quad

		high_triple = highest_triple(sorted)
		low_pair = highest_pair(sorted, high_triple)
		if high_triple != NONE and low_pair != NONE:
			return 'H' + high_triple +  low_pair
	
	# ignore straight flush atm
	high_flush = highest_flush(sorted)
	if (high_flush != NONE):
		return 'F' + high_flush
	
	high_straight = highest_straight(sorted)
	if (high_straight != NONE):
		return 'S' + high_straight

	if (high_triple != NONE):
		return 'T' + high_triple

	if (high_pair != NONE):
		low_pair = highest_pair(sorted, high_pair)
		if (low_pair != NONE):
			return 'D' + high_pair + low_pair

		return 'P' + high_pair

	return 'C' + sorted[len(sorted) - 1][0]

# compare hands from bestHand()
def compare_hands(one: str, two: str) -> int:
	mapping = {
		'C': 0,
		'P': 1,
		'D': 2,
		'T': 3,
		'S': 4,
		'F': 5,
		'H': 6,
		'Q': 7,
	}

	if one[0] == two[0]: # same type of hand
		for i in range(1, len(one)):
			if cton[one[i]] > cton[two[i]]:
				return 1
			elif cton[one[i]] < cton[two[i]]:
				return -1
				
	elif (mapping[one[0]] > mapping[two[0]]):
		return 1
	
	elif (mapping[one[0]] < mapping[two[0]]):
		return -1
	
	return 0

def draw_random_cards(cards: list, num: int):
	drawn_cards = []
	length = len(cards)

	already_chosen_indices = set()
	for _ in range(num):
		index = random.randrange(length)
		while index in already_chosen_indices:
			index = random.randrange(length)
		already_chosen_indices.add(index)
		drawn_cards.append(cards[index])

	return drawn_cards

# evaluate hand strength at anytime in the game using Monte-Carlo sim
def monte_carlo_prob(hole_cards: list, shared_cards: list, remaining_cards: list = [], iters: int = 200) -> float:
	if remaining_cards == []:
		remaining_cards = all_cards_excluding(hole_cards + shared_cards)

	# print(f"Monte Carlo can see {len(shared_cards)} community cards")
	above = 0 # hands that beat ours
	below = 0 # hands that ours beats
	equiv = 0 # hands that are equivalent to ours
	prob = 0

	if len(shared_cards) == 0:
		sorted = sort_cards(hole_cards)
		if hole_cards[0][1] == hole_cards[1][1]:
			prob = float(hole_strengths[str(sorted[1][0] + sorted[0][0] + 's')])
		else:
			prob = float(hole_strengths[str(sorted[1][0] + sorted[0][0] + 'o')])

	else:
		for _ in range(iters):
			drawn_cards = draw_random_cards(remaining_cards, 7 - len(shared_cards))

			# future_shared is the possible
			future_shared = shared_cards + drawn_cards[2:]

			pool = future_shared + hole_cards
			opp_pool = future_shared + drawn_cards[:2]

			hand = eval7.evaluate([eval7.Card(card) for card in pool])
			opp_hand = eval7.evaluate([eval7.Card(card) for card in opp_pool])
			if hand > opp_hand:
				above += 1
			elif hand < opp_hand:
				below += 1
			else:
				equiv += 1

		wins = float(above + (equiv / 2.0))

		assert(above + below + equiv == iters)
		total = float(above + below + equiv)
		prob = wins / total

	if (len(shared_cards) == 0):
		print(f"[{' '.join(hole_cards)}]: {round(prob, 2)}.")
	else:
		print(f"[{' '.join(hole_cards)}] on [{' '.join(shared_cards)}]: {round(prob, 2)}.")

	return prob
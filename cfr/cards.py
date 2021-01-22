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
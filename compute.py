from cards import all_cards_excluding, draw_random_cards
import csv
import eval7

# evaluate hand strength at anytime in the game using Monte-Carlo sim
def monte_carlo_prob(hole_cards: list, shared_cards: list, remaining_cards: list = [], iters: int = 50) -> float:
	if remaining_cards == []:
		remaining_cards = all_cards_excluding(hole_cards + shared_cards)

	# print(f"Monte Carlo can see {len(shared_cards)} community cards")
	above = 0 # hands that beat ours
	below = 0 # hands that ours beats
	equiv = 0 # hands that are equivalent to ours

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

	return wins/total

diamonds = ('Ad', 'Kd', 'Qd', 'Jd', 'Td', '9d', '8d', '7d', '6d', '5d', '4d', '3d', '2d')
hearts = ('Ah', 'Kh', 'Qh', 'Jh', 'Th', '9h', '8h', '7h', '6h', '5h', '4h', '3h', '2h')

holes = {}

# calculate all suited
for i in range(len(diamonds)):
    for j in range(i + 1, len(diamonds)):
        holes[str(diamonds[i][0] + diamonds[j][0] + 's')] = monte_carlo_prob([diamonds[i], diamonds[j]], [], [], iters=100000)

# calculate all not suited
for i in range(len(diamonds)):
    for j in range(i, len(hearts)):
        holes[str(diamonds[i][0] + hearts[j][0] + 'o')] = monte_carlo_prob([diamonds[i], hearts[j]], [], [], iters=100000)

file = open('hole_strengths.csv', 'w')
writer = csv.DictWriter(file, ['hole cards', 'strength'])
writer.writeheader()
for key in holes:
    writer.writerow({ 'hole cards': key, 'strength': holes[key] })
file.close()
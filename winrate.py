from ..cards import all_cards_excluding, draw_random_cards, monte_carlo_prob
import csv
import eval7

# evaluate hand strength at anytime in the game using Monte-Carlo sim
def win_rate(hole_cards: list, opp_hole_cards:list, shared_cards: list, iters: int = 500) -> float:
	remaining_cards = all_cards_excluding(hole_cards + opp_hole_cards + shared_cards)

	# print(f"Monte Carlo can see {len(shared_cards)} community cards")
	above = 0 # hands that beat ours
	below = 0 # hands that ours beats
	equiv = 0 # hands that are equivalent to ours

	for _ in range(iters):
		drawn_cards = draw_random_cards(remaining_cards, 5 - len(shared_cards))

		# future_shared is the possible
		future_shared = shared_cards + drawn_cards

		pool = future_shared + hole_cards
		opp_pool = future_shared + opp_hole_cards

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

all_cards = all_cards_excluding()
middle = draw_random_cards(all_cards, 5)
holes = []

for k in range(1000):
	remaining = all_cards_excluding(middle)
	hole = draw_random_cards(remaining, 2)
	opp_pool = all_cards_excluding(hole + middle)
	opp = draw_random_cards(opp_pool, 2)
	hole_pool = all_cards_excluding(opp + middle)

	cards = all_cards_excluding(hole + opp)
	diff = monte_carlo_prob(hole, []) - monte_carlo_prob(opp, [])

	holes += [[diff, win_rate(hole, opp, [])]]

file = open('diff vs winrate.csv', 'w')
writer = csv.DictWriter(file, ['diff', 'winrate'])
writer.writeheader()
for el in holes:
	print(el)
	writer.writerow({ 'diff': el[0], 'winrate': el[1] })
file.close()
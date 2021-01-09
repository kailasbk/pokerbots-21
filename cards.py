import random

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

def createCards(excludes):
	cards = []

	for value in VALUES:
		for suit in SUITS:
			card = value + suit
			if card not in excludes:
				cards.append(card)

	return cards

def sortCards(cards):
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
def highestPair(cards, exclude = NONE):
	highest = NONE

	for i in range(len(cards) - 1):
		if cards[i][0] != exclude and cards[i][0] == cards[i + 1][0]:
			highest = cards[i][0]

	return highest

# assume sorted
def highestTriple(cards, exclude = NONE):
	highest = NONE

	for i in range(len(cards) - 2):
		if cards[i][0] != exclude and cards[i][0] == cards[i + 2][0]:
			highest = cards[i][0]

	return highest

# assume sorted
def highestQuad(cards):
	highest = NONE

	for i in range(len(cards) - 3):
		if cards[i][0] == cards[i + 3][0]:
			highest = cards[i][0]

	return highest

# assume sorted
def highestFlush(cards):
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
def highestStraight(cards):
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
def bestHand(cards):
	if (len(cards) == 0):
		return ''
	
	sorted = sortCards(cards)

	highPair = highestPair(sorted)
	lowPair = NONE
	highTriple = NONE
	if highPair != NONE:
		highQuad = highestQuad(sorted)
		if highQuad != NONE:
			return 'Q' + highQuad

		highTriple = highestTriple(sorted)
		lowPair = highestPair(sorted, highTriple)
		if highTriple != NONE and lowPair != NONE:
			return 'H' + highTriple +  lowPair
	
	# ignore straight flush atm
	highFlush = highestFlush(sorted)
	if (highFlush != NONE):
		return 'F' + highFlush
	
	highStraight = highestStraight(sorted)
	if (highStraight != NONE):
		return 'S' + highStraight

	if (highTriple != NONE):
		return 'T' + highTriple

	if (highPair != NONE):
		lowPair = highestPair(sorted, highPair)
		if (lowPair != NONE):
			return 'D' + highPair + lowPair

		return 'P' + highPair

	return 'C' + sorted[len(sorted) - 1][0]

# compare hands from bestHand()
def compareHands(one, two):
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

	if one[0] == two[0]:
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


# evaluate hand strength at anytime in the game using Monte-Carlo sim
def MonteCarloProb(hole, middle, remaining):
	above = 0
	below = 0
	equiv = 0

	for k in range(50):
		i = random.randrange(len(remaining))
		j = random.randrange(len(remaining))
		while (i == j):
			j = random.randrange(len(remaining))

		oppHole = [remaining[i], remaining[j]]

		future = middle

		if len(middle) == 3:
			g = random.randrange(len(remaining))
			h = random.randrange(len(remaining))
			while g == i or g == j:
				g = random.randrange(len(remaining))
			while h == i or h == j or h == g:
				h = random.randrange(len(remaining))
			
			future.append(remaining[g])
			future.append(remaining[h])

		if len(middle) == 4:
			g = random.randrange(len(remaining))
			while g == i or g == j:
				g = random.randrange(len(remaining))
			
			future.append(remaining[g])

		pool = []
		oppPool = []
		for card in future:
			pool.append(card)
			oppPool.append(card)

		for i in range(2):
			pool.append(hole[i])
			oppPool.append(oppHole[i])

		hand = bestHand(pool)
		opp = bestHand(oppPool)
		if compareHands(hand, opp) > 0:
			above += 1
		elif compareHands(hand, opp) < 0:
			below += 1
		else:
			equiv += 1

	wins = float(above + (equiv/2.0))
	total = float(above + below + equiv)
	print("Results: {} wins / {}. Win probability: {}.".format(wins, total, wins/total));
	return wins/total
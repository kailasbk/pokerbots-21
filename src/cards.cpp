#include "cards.h"

int cton(char value, bool aceLower)
{
	static std::map<char, int> mapping = {
		std::pair<char, int>('2', 2),
		std::pair<char, int>('3', 3),
		std::pair<char, int>('4', 4),
		std::pair<char, int>('5', 5),
		std::pair<char, int>('6', 6),
		std::pair<char, int>('7', 7),
		std::pair<char, int>('8', 8),
		std::pair<char, int>('9', 9),
		std::pair<char, int>('T', 10),
		std::pair<char, int>('J', 11),
		std::pair<char, int>('Q', 12),
		std::pair<char, int>('K', 13),
		std::pair<char, int>('A', 14),
	};

	if (aceLower)
	{
		mapping['A'] = 1;
	}
	else
	{
		mapping['A'] = 14;
	}

	return mapping[value];
}

char ntoc(int value)
{
	static std::map<int, char> mapping = {
		std::pair<int, char>(1, 'A'),
		std::pair<int, char>(2, '2'),
		std::pair<int, char>(3, '3'),
		std::pair<int, char>(4, '4'),
		std::pair<int, char>(5, '5'),
		std::pair<int, char>(6, '6'),
		std::pair<int, char>(7, '7'),
		std::pair<int, char>(8, '8'),
		std::pair<int, char>(9, '9'),
		std::pair<int, char>(10, 'T'),
		std::pair<int, char>(11, 'J'),
		std::pair<int, char>(12, 'Q'),
		std::pair<int, char>(13, 'K'),
		std::pair<int, char>(14, 'A'),
	};

	return mapping[value];
}

std::vector<Card> createCards(std::vector<Card> excludes)
{
	std::vector<Card> cards;
	cards.reserve(52 - excludes.size());

	std::string excludeString = "";
	for (Card card : excludes)
	{
		excludeString += card;
	}

	for (char value : VALUES)
	{
		for (char suit : SUITS)
		{
			Card card = std::string({value, suit});

			if (excludeString.find(card) == std::string::npos)
			{
				cards.push_back(card);
			}
		}
	}

	return cards;
}

std::vector<Card> sortCards(std::vector<Card> cards)
{
	for (int i = 0; i < cards.size(); i++)
	{
		int k = i;
		for (int j = i; j < cards.size(); j++)
		{
			if (cton(cards[j][0]) < cton(cards[k][0]))
			{
				k = j;
			}
		}

		Card temp = cards[i];
		cards[i] = cards[k];
		cards[k] = temp;
	}

	return cards;
}

// assume sorted
char highestPair(std::vector<Card> cards, char exclude)
{
	char highest = NONE;

	for (int i = 0; i < cards.size() - 1; i++)
	{
		if (cards[i][0] != exclude && cards[i][0] == cards[i + 1][0])
		{
			highest = cards[i][0];
		}
	}

	return highest;
}

// assume sorted
char highestTriple(std::vector<Card> cards, char exclude)
{
	char highest = NONE;

	for (int i = 0; i < cards.size() - 2; i++)
	{
		if (cards[i][0] != exclude && cards[i][0] == cards[i + 2][0])
		{
			highest = cards[i][0];
		}
	}

	return highest;
}

// assume sorted
char highestQuad(std::vector<Card> cards)
{
	char highest = NONE;

	// casting to int to avoid unsigned long overflow (-1)
	for (int i = 0; i < (int)cards.size() - 3; i++)
	{
		if (cards[i][0] == cards[i + 3][0])
		{
			highest = cards[i][0];
		}
	}

	return highest;
}

// assume sorted
char highestFlush(std::vector<Card> cards)
{
	char highest = NONE;

	for (char suit : SUITS)
	{
		int count = 0;
		char potential = '2';
		for (Card card : cards)
		{
			if (card[1] == suit)
			{
				count++;
				if (cton(potential) < cton(card[0]))
				{
					potential = card[0];
				}
			}
		}
		if (count >= 5)
		{
			highest = potential;
		}
	}

	return highest;
}

// assume sorted
char highestStraight(std::vector<Card> cards)
{
	char highest = NONE;

	for (int i = 0; i < cards.size(); i++)
	{
		int count = 0;
		char potential = NONE;
		for (int j = i; j < cards.size() - 1; j++)
		{
			int diff = cton(cards[j + 1][0]) - cton(cards[j][0]);
			if (diff == 1)
			{
				potential = cards[j + 1][0];
				count++;
			}
			else if (diff == 0)
			{
				// pass
			}
			else
			{
				break;
			}
		}
		if (count >= 5)
		{
			highest = potential;
		}
	}

	return highest;
}

// dont assume sorted
std::string bestHand(std::vector<Card> cards)
{
	if (cards.empty())
	{
		return "";
	}
	std::vector<Card> sorted = sortCards(cards);

	char highPair = highestPair(sorted);
	char lowPair = NONE;
	char highTriple = NONE;
	if (highPair != NONE)
	{
		char highQuad = highestQuad(sorted);
		if (highQuad != NONE)
		{
			return std::string{'Q', highQuad};
		}

		highTriple = highestTriple(sorted);
		lowPair = highestPair(sorted, highTriple);
		if (highTriple != NONE && lowPair != NONE)
		{
			return std::string{'H', highTriple, lowPair};
		}
	}

	// ignore straight flush atm
	char highFlush = highestFlush(sorted);
	if (highFlush != NONE)
	{
		return std::string{'F', highFlush};
	}
	char highStraight = highestStraight(sorted);
	if (highStraight != NONE)
	{
		return std::string{'S', highStraight};
	}

	if (highTriple != NONE)
	{
		return std::string{'T', highTriple};
	}

	if (highPair != NONE)
	{
		lowPair = highestPair(sorted, highPair);
		if (lowPair != NONE)
		{
			return std::string{'D', highPair, lowPair};
		}
		return std::string{'P', highPair};
	}

	return std::string{'C', sorted.back()[0]};
}

// compare hands from bestHand()
int compareHands(std::string one, std::string two)
{
	static std::map<char, int> mapping = {
		std::pair<char, int>('C', 0),
		std::pair<char, int>('P', 1),
		std::pair<char, int>('D', 2),
		std::pair<char, int>('T', 3),
		std::pair<char, int>('S', 4),
		std::pair<char, int>('F', 5),
		std::pair<char, int>('H', 6),
		std::pair<char, int>('Q', 7),
	};

	if (one[0] == two[0])
	{
		for (int i = 1; i < one.length(); i++)
		{
			if (cton(one[i]) > cton(two[i]))
			{
				return 1;
			}
			else if (cton(one[i]) < cton(two[i]))
			{
				return -1;
			}
		}
	}
	else if (mapping[one[0]] > mapping[two[0]])
	{
		return 1;
	}
	else if (mapping[one[0]] < mapping[two[0]])
	{
		return -1;
	}
	return 0;
}

// evaluate hand strength at anytime in the game using Monte-Carlo sim
double MonteCarloProb(std::array<Card, 2> hole, std::vector<Card> middle, std::vector<Card> remaining)
{
	int above = 0, below = 0, equiv = 0;

	for (int k = 0; k < 100; k++)
	{
		int i = rand() % remaining.size();
		int j = rand() % remaining.size();
		while (i == j)
		{
			j = rand() % remaining.size();
		}

		std::array<Card, 2> oppHole = {remaining[i], remaining[j]};
		std::array<std::array<Card, 2>, 2> holes = {hole, oppHole};

		std::vector<Card> future = middle;
		future.reserve(5);

		if (middle.size() == 3)
		{
			int g = rand() % remaining.size();
			int h = rand() % remaining.size();
			while (g == i || g == j)
			{
				g = rand() % remaining.size();
			}
			while (h == i || h == j || h == g)
			{
				h = rand() % remaining.size();
			}
			future.push_back(remaining[g]);
			future.push_back(remaining[h]);
		}

		if (middle.size() == 4) {
			int g = rand() % remaining.size();
			while (g == i || g == j)
			{
				g = rand() % remaining.size();
			}
			future.push_back(remaining[g]);
		}
		
		std::array<std::vector<Card>, 2> pools;
		for (int i = 0; i < 2; i++)
		{
			std::vector<Card> pool;
			pool.reserve(7);
			for (Card card : future)
			{
				pool.push_back(card);
			}
			for (Card card : holes[i])
			{
				pool.push_back(card);
			}

			pools[i] = pool;
		}

		std::string hand = bestHand(pools[0]);
		std::string opp = bestHand(pools[1]);
		if (compareHands(hand, opp) > 0)
		{
			above++;
		}
		else if (compareHands(hand, opp) < 0)
		{
			below++;
		}
		else
		{
			equiv++;
		}
	}

	fmt::print("There are {} wins out of {} attempts \n", above, (above + below + equiv));
	return (float)above / (above + below + equiv);
}
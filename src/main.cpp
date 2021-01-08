#include <skeleton/actions.h>
#include <skeleton/constants.h>
#include <skeleton/runner.h>
#include <skeleton/states.h>

#include <vector>
#include <array>
#include <map>
#include <string>
#include <fmt/core.h>

#include "cards.h"

using namespace pokerbots::skeleton;

double prob(RoundStatePtr roundState, int i, int active)
{
	const BoardState *board_ptr = static_cast<const BoardState *>(roundState->boardStates[i].get());

	std::array<Card, 2> hand = board_ptr->hands[active];
	std::array<Card, 5> deck = board_ptr->deck;

	std::vector<Card> pool = {hand[0], hand[1]};
	std::vector<Card> middle;

	for (Card card : deck)
	{
		if (card != "")
		{
			pool.push_back(card);
			middle.push_back(card);
		}
	}

	std::vector<Card> remaining = createCards(pool);

	return MonteCarloProb(hand, middle, remaining);
}

struct Bot
{
	std::array<Card, 6> cards;

	void handleNewRound(GameInfoPtr gameState, RoundStatePtr roundState, int active)
	{
		cards = roundState->hands[active];
		std::vector<Card> unsorted;
		unsorted.reserve(6);
		for (Card card: cards)
		{
			unsorted.push_back(card);
		}
		std::vector<Card> sorted = sortCards(unsorted);
		for (int i = 0; i < 6; i++)
		{
			cards[i] = sorted[i];
		}
	}

	void handleRoundOver(GameInfoPtr gameState, TerminalStatePtr terminalState, int active)
	{
		fmt::print("----------END ROUND {}----CLOCK:{}----------\n", gameState->roundNum, gameState->gameClock);
	}

	std::vector<Action> getActions(GameInfoPtr gameState, RoundStatePtr roundState, int active)
	{
		auto legalActions = roundState->legalActions();
		std::vector<Action> myActions;
		for (int i = 0; i < NUM_BOARDS; i++)
		{
			// if assign action is legal
			if (legalActions[i].find(Action::Type::ASSIGN) != legalActions[i].end())
			{
				// assign the cards to the board sequentially from sorted cards
				myActions.emplace_back(
					Action::Type::ASSIGN,
					std::array<Card, 2>{cards[2 * i], cards[2 * i + 1]});
			}
			else 
			{
				const BoardStatePtr board_ptr = std::static_pointer_cast<const BoardState>(roundState->boardStates[i]);
				int stack = roundState->stacks[active];
				int continueCost = board_ptr->pips[(1 + active) % 2] - board_ptr->pips[active];
				int pot = board_ptr->pot;
				double potOdds = (double)continueCost / (pot + continueCost);
				double winProb = prob(roundState, i, active);
				
				// if they haven't raised and we can raise
				if (winProb >= .8 && legalActions[i].find(Action::Type::RAISE) != legalActions[i].end())
				{
					if (BIG_BLIND <= 3 * BIG_BLIND &&  3 * BIG_BLIND <= stack)
					{
						myActions.emplace_back(Action::Type::RAISE, 3 * BIG_BLIND);
					}
					else
					{
						myActions.emplace_back(Action::Type::RAISE, stack);
					}
				}
				// if opponent just raised (call and fold, maybe raise, are legal)
				else if (legalActions[i].find(Action::Type::CALL) != legalActions[i].end())
				{
					// check on the board
					if (winProb > potOdds)
					{
						myActions.emplace_back(Action::Type::CALL);
					}
					else 
					{
						// change to fold when possible
						myActions.emplace_back(Action::Type::CALL);
					}
				}
				// if its not worth raising, just check
				else if (legalActions[i].find(Action::Type::CHECK) != legalActions[i].end())
				{
					// else check on the board
					myActions.emplace_back(Action::Type::CHECK);
				}
			}
		}
		return myActions;
	}
};

int main(int argc, char *argv[])
{
	auto host = parseArgs(argc, argv)[0];
	auto port = parseArgs(argc, argv)[1];
	runBot<Bot>(host, port);
	return 0;
}

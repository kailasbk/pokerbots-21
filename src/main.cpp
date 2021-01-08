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

	std::vector<Card> sorted = sortCards(pool);
	std::string handType = bestHand(pool);
	fmt::print("The sorted pool is {}. Best hand is {}. \n", fmt::join(sorted, ", "), handType);

	std::vector<Card> remaining = createCards(pool);

	return MonteCarloProb(hand, middle, remaining);
}

struct Bot
{
	void handleNewRound(GameInfoPtr gameState, RoundStatePtr roundState, int active)
	{
	}

	void handleRoundOver(GameInfoPtr gameState, TerminalStatePtr terminalState, int active)
	{
		fmt::print("----------END ROUND {}----CLOCK:{}----------\n", gameState->roundNum, gameState->gameClock);
	}

	std::vector<Action> getActions(GameInfoPtr gameState, RoundStatePtr roundState, int active)
	{
		auto legalActions = roundState->legalActions();
		auto myCards = roundState->hands[active];
		std::vector<Action> myActions;
		myActions.reserve(NUM_BOARDS);
		for (int i = 0; i < NUM_BOARDS; i++)
		{
			// if assign action is legal
			if (legalActions[i].find(Action::Type::ASSIGN) != legalActions[i].end())
			{
				// assign the cards to the board sequentially
				myActions.emplace_back(
					Action::Type::ASSIGN,
					std::array<Card, 2>{myCards[2 * i], myCards[2 * i + 1]});
			}
			// if you have a pair
			else if (prob(roundState, i, active) >= .7 && legalActions[i].find(Action::Type::RAISE) != legalActions[i].end())
			{
				myActions.emplace_back(Action::Type::RAISE, 3 * BIG_BLIND);
			}
			// if the check action is legal
			else if (legalActions[i].find(Action::Type::CHECK) != legalActions[i].end())
			{
				// check on the board
				myActions.emplace_back(Action::Type::CHECK);
			}
			else
			{
				// call on the board (always legal if check is not)
				myActions.emplace_back(Action::Type::CALL);
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

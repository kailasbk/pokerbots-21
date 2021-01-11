from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, AssignAction
from skeleton.states import GameState, TerminalState, RoundState, BoardState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND, NUM_BOARDS
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from cards import *
from typing import List

class Player(Bot):
	'''
	A pokerbot.
	'''

	def __init__(self):
		'''
		Called when a new game starts. Called exactly once.

		Arguments:
		Nothing.

		Returns:
		Nothing.
		'''
		self.cards = []
		pass

	def allocate_cards(self):
		"""Allocates the six hole cards by pair-hunting and sorting the 
		remaining singles

		Args:
			None.

		Returns:
			A list of NUM_BOARDS pairs of cards, in order of singles of 
			increasing rank, then pairs of increasing rank
		"""
		cards = sort_cards(self.cards)
		assert(len(cards) == 2 * NUM_BOARDS)

		ranks = {}
		for card in cards:
			if card[0] in ranks:
				ranks[card[0]] += [card]
			else:
				ranks[card[0]] = [card]
		
		pairs = []
		singles = []
		for rank in ranks:
			while len(ranks[rank]) >= 2:
				pairs.append([ranks[rank].pop(), ranks[rank].pop()])
			assert(len(ranks[rank]) == 0 or len(ranks[rank]) == 1)

			singles += ranks[rank]
			ranks[rank].clear()
			assert(len(ranks[rank]) == 0)

		assert(len(singles) % 2 == 0)
		pairs_of_singles = []
		for i in range(len(singles) // 2):
			pairs_of_singles.append([singles[2 * i], singles[2 * i + 1]])

		assert(len(pairs_of_singles) + len(pairs) == NUM_BOARDS)
		return pairs_of_singles + pairs

		# naive: sequentially allocated cards
		# return [[self.cards[2 * i], self.cards[2 * i + 1]] for i in range(NUM_BOARDS)]

	def win_probability(self, board_state: BoardState, active: int):
		hole_cards = board_state.hands[active] # the two hole cards for this board

		seen_cards = self.cards # so far, the 2 * NUM_BOARDS cards in our holes
		shared_cards = []

		print(f"These are the community cards from board_state.deck: {board_state.deck}")
		for card in board_state.deck: # all community cards
			if card != '': # community card has been revealed
				seen_cards.append(card) 
				shared_cards.append(card)
		print(f"These are the shared cards (nonempty cards from board_state.deck): {shared_cards}")

		remaining_cards = all_cards_excluding(seen_cards)

		return monte_carlo_prob(hole_cards, shared_cards, remaining_cards)

	def handle_new_round(self, game_state: GameState, round_state: RoundState, active: int):
		'''
		Called when a new round starts. Called NUM_ROUNDS times.

		Arguments:
		game_state: the GameState object.
		round_state: the RoundState object.
		active: your player's index.

		Returns:
		Nothing.
		'''
		self.cards = round_state.hands[active]
		print(f"----------BEGIN ROUND {game_state.round_num}--CLOCK:{game_state.game_clock}----------")
		print(f"My cards are {self.cards}")

		self.card_allocation = self.allocate_cards()
		print(f"My card allocation is {self.card_allocation}")
		pass

	def handle_round_over(self, game_state: GameState, terminal_state: TerminalState, active: int):
		'''
		Called when a round ends. Called NUM_ROUNDS times.

		Arguments:
		game_state: the GameState object.
		terminal_state: the TerminalState object.
		active: your player's index.

		Returns:
		Nothing.
		'''
		print(f"----------END ROUND {game_state.round_num}----CLOCK:{game_state.game_clock}----------")
		pass

	def get_actions(self, game_state: GameState, round_state: RoundState, active: int):
		'''
		Where the magic happens - your code should implement this function.
		Called any time the engine needs a triplet of actions from your bot.

		Arguments:
		game_state: the GameState object.
		round_state: the RoundState object.
		active: your player's index.

		Returns:
		Your actions.
		'''
		legal_actions = round_state.legal_actions()
		my_actions = [None] * NUM_BOARDS
		stack = round_state.stacks[active]

		# cards = self.allocate_cards()

		for i in range(NUM_BOARDS):
			if AssignAction in legal_actions[i]:
				my_actions[i] = AssignAction(self.card_allocation[i])

			else:
				board_state = round_state.board_states[i]

				if isinstance(board_state, TerminalState):
					my_actions[i] = CheckAction()
					continue

				continue_cost = board_state.pips[1-active] - board_state.pips[active]
				pot = board_state.pot
				pot_odds = float(continue_cost) / (pot + continue_cost)
				win_prob = self.win_probability(board_state, active)
				
				# if they haven't raised and we can raise
				if win_prob >= .7 and RaiseAction in legal_actions[i] and stack != 0:
					# increase = (3 * BIG_BLIND)
					increase = max((3 * BIG_BLIND), int(0.5 * pot))
					# increase = int(0.5 * pot)
					amount = board_state.pips[1-active] + increase
					# if can bet normally
					if stack > increase + continue_cost and board_state.pips[active] < 30:
						print(f'Betting/raising on board {i + 1} to {amount}.')
						my_actions[i] = RaiseAction(amount)
						stack -= amount
					# otherwise (don't do all in rn)
					else:
						if CallAction in legal_actions[i]:
							print(f'Calling on board {i + 1}.')
							my_actions[i] = CallAction()
						elif CheckAction in legal_actions[i]:
							print(f'Checking on board {i + 1}.')
							my_actions[i] = CheckAction()

				# if opponent just raised (call and fold, maybe raise, are legal)
				elif CallAction in legal_actions[i]:
					# check on the board
					if (win_prob > pot_odds):
						print(f'Pot odds: {pot_odds}')
						print(f'Calling on board {i + 1}.')
						my_actions[i] = CallAction()
					else:
						print(f'Pot odds: {pot_odds}')
						print(f'Folding on board {i + 1}.')
						my_actions[i] = FoldAction()

				# if its not worth raising, just check
				elif CheckAction in legal_actions[i]:
					# else check on the board
					print(f'Checking on board {i + 1}.')
					my_actions[i] = CheckAction()
		print()
		return my_actions

if __name__ == '__main__':
	run_bot(Player(), parse_args())
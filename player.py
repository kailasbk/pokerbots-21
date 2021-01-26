from typing import cast
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, AssignAction
from skeleton.states import GameState, TerminalState, RoundState, BoardState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND, NUM_BOARDS
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

from cards import *
from cfr.tree import create_game_tree, branches_from_dealer, raise_branches
from cfr.nodes import *
from cfr.player import Player as CFRPlayer
import json

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
		self.tree = create_game_tree()
		print('Loading strategy...')
		f = open('strategy.json', 'r')
		strategy = json.load(f)
		for i in range(len(Node.all_nodes)):
			Node.all_nodes[i].set_strategy(strategy[i])
		print('Strategy loaded!')

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

		# print(f"These are the community cards from board_state.deck: {board_state.deck}")
		for card in board_state.deck: # all community cards
			if card != '': # community card has been revealed
				seen_cards.append(card) 
				shared_cards.append(card)
		# print(f"These are the shared cards (nonempty cards from board_state.deck): {shared_cards}")

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
		print(f"---BEGIN ROUND {game_state.round_num}--CLOCK:{round(game_state.game_clock, 2)}---")
		print(f"My cards are {self.cards}")

		self.card_allocation = self.allocate_cards()
		print(f"My card allocation is {self.card_allocation}")

		name = 'SB' if active == 0 else 'BB'
		self.players = [CFRPlayer(name, self.tree, self.card_allocation[i]) for i in range(NUM_BOARDS)]
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
		previous_state: RoundState = terminal_state.previous_state
		for i in range(3):
			opp_hand = previous_state.board_states[i].previous_state.hands[1-active]
			if opp_hand != ['', '']:
				print(f"Shown [{' '.join(opp_hand)}] on board {i + 1}")
		
		print(f"---END ROUND {game_state.round_num}----CLOCK:{round(game_state.game_clock, 2)}---")
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
		raise_bounds = list(round_state.raise_bounds())

		for i in range(NUM_BOARDS):
			board_state = round_state.board_states[i]

			if isinstance(board_state, TerminalState):
				my_actions[i] = CheckAction()
				continue

			elif board_state.settled:
				my_actions[i] = CheckAction()
				continue

			elif AssignAction in legal_actions[i]:
				my_actions[i] = AssignAction(self.card_allocation[i])

			elif round_state.street <= 3:
				print(f'-Board {i+1}-')
				pips = board_state.pips[active]
				opp_pips = board_state.pips[1-active]
				continue_cost = opp_pips - pips
				while not self.players[i].is_owner():
					if self.players[i].current_node().get_owner() == 'D':
						mc = self.win_probability(board_state, active)
						for hand_range in branches_from_dealer:
							if mc <= float(hand_range):
								self.players[i].move_down(hand_range)
								print(f'Branching from dealer: {hand_range}')
								break
					else:
						prev = self.players[i].current_node().get_incoming()
						if continue_cost > 0:
							raise_amounts = [int(action[1:]) for action in raise_branches]
							casted_amount = 0
							for amount in raise_amounts:
								if continue_cost <= amount:
									casted_amount = amount
									break
							if casted_amount == 0: 
								casted_amount = raise_amounts[-1]

							if 'R' in prev:
								self.players[i].move_down(f'RR{casted_amount}')
								print(f'Opp chose branch: RR{casted_amount}')
							else:
								self.players[i].move_down(f'R{casted_amount}')
								print(f'Opp chose branch: R{casted_amount}')
						else:
							if 'R' in prev:
								self.players[i].move_down('C')
								print('Opp chose branch: C')
							elif 'K1' == prev or 'C' == prev:
								self.players[i].move_down('K2')
								print('Opp chose branch: K2')
							elif '.' in prev:
								if 'K1' in self.players[i].get_branches():
									self.players[i].move_down('K1')
									print('Opp chose branch: K1')
								elif 'C' in self.players[i].get_branches():
									self.players[i].move_down('C')
									print('Opp chose branch: C')

				branch = self.players[i].choose_branch()
				prev = self.players[i].current_node().get_incoming()
				if 'RR' in branch and CallAction in legal_actions[i]:
					my_actions[i] = CallAction()
					self.players[i].move_down('C')
					print('Choosing branch: C')
				elif 'R' in branch and RaiseAction in legal_actions[i]:
					raise_amount = min(raise_bounds[1], int(branch[1:]))
					raise_bounds[1] -= raise_amount
					my_actions[i] = RaiseAction(raise_amount + opp_pips)
					self.players[i].move_down(branch)
					print('Choosing branch:', branch)
				elif 'C' in branch and CallAction in legal_actions[i]:
					my_actions[i] = CallAction()
					self.players[i].move_down(branch)
					print('Choosing branch:', branch)
				elif 'K' in branch and CheckAction in legal_actions[i]:
					my_actions[i] = CheckAction()
					self.players[i].move_down(branch)
					print('Choosing branch:', branch)
				elif 'F' in branch and FoldAction in legal_actions[i]:
					my_actions[i] = FoldAction()
					self.players[i].move_down(branch)
					print('Choosing branch:', branch)

			else:				
				pips = board_state.pips[active]
				opp_pips = board_state.pips[1-active]
				continue_cost = opp_pips - pips
				pot = board_state.pot + opp_pips + pips
				pot_odds = float(continue_cost) / (pot + continue_cost)
				win_prob = self.win_probability(board_state, active)

				if continue_cost == 0:
					if win_prob >= .7 and RaiseAction in legal_actions[i] and stack != 0:
						if win_prob >= 0.9:
							increase = max((3 * BIG_BLIND), int(0.75 * pot))
						else:
							increase = max((3 * BIG_BLIND), int(0.5 * pot))
							
						# increase = max((3 * BIG_BLIND), int(0.5 * pot))

						amount = board_state.pips[1-active] + increase
						# if can bet normally
						if stack > increase + continue_cost:
							print(f'Bet/raise board {i + 1} to {amount}.')
							my_actions[i] = RaiseAction(amount)
							stack -= amount
						# otherwise (don't do all in rn)
						else:
							print(f'Check board {i + 1}.')
							my_actions[i] = CheckAction()
						# if its not worth raising, just check
					else:
						# else check on the board
						print(f'Check board {i + 1}.')
						my_actions[i] = CheckAction()	
				
				else:
					if pips == 1: # our first move as small blind
						if win_prob > pot_odds:
							print(f'Call board {i + 1} w/ {round(pot_odds, 2)} odds.')
							my_actions[i] = CallAction()
						else:
							print(f'Fold board {i + 1}')
							my_actions[i] = FoldAction()

					elif win_prob - .5 > pot_odds or win_prob > .95 - (.05 * (5 - round_state.street)):
						# second condition is to protect against all-in bots
						print(f'Call board {i + 1} w/ {round(pot_odds, 2)} odds.')
						my_actions[i] = CallAction()
						
					else:
						print(f'Fold board {i + 1}')
						my_actions[i] = FoldAction()

		print()
		return my_actions

if __name__ == '__main__':
	run_bot(Player(), parse_args())
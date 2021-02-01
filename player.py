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
		self.offsets = [.4, .4, .4]
		self.when_raised = [[]] * 3
		self.tree = create_game_tree()
		self.clinched = False
		print('Loading strategy...')
		f = open('strats/strategy1000000.json', 'r')
		strategy = json.load(f)
		assert len(strategy) == Node.number_of_nodes()
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

	def win_probability(self, board_state: BoardState, active: int):
		hole_cards = board_state.hands[active] # the two hole cards for this board

		seen_cards = self.cards # so far, the 2 * NUM_BOARDS cards in our holes
		shared_cards = []

		for card in board_state.deck: # all community cards
			if card != '': # community card has been revealed
				seen_cards.append(card) 
				shared_cards.append(card)

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
		print(f"My call offsets: {self.offsets}")
		print(f"My cards are {self.cards}")

		self.card_allocation = self.allocate_cards()
		print(f"My card allocation is {self.card_allocation}")

		name = 'SB' if active == 0 else 'BB'
		self.players = [CFRPlayer(name, self.tree, self.card_allocation[i]) for i in range(NUM_BOARDS)]
		self.when_raised = [[]] * 3
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
			shared_cards = previous_state.board_states[i].previous_state.deck
			if opp_hand != ['', '']:
				print(f"Shown [{' '.join(opp_hand)}] on board {i + 1}")
				eval_shared = [eval7.Card(card) for card in shared_cards]
				opp = eval7.evaluate(eval_shared + [eval7.Card(card) for card in opp_hand])
				me = eval7.evaluate(eval_shared + [eval7.Card(card) for card in self.card_allocation[i]])
				print(self.card_allocation[i])
				if self.when_raised[i] != []:
					if opp > me:
						self.offsets[i] += .01
					elif opp < me:
						self.offsets[i] -= .01
					
					if self.offsets[i] < .1:
						self.offsets[i] = .1
					elif self.offsets[i] > .7:
						self.offsets[i] = .7
		
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
		raise_bounds = list(round_state.raise_bounds())
		print(raise_bounds)
		total_cost = sum([(round_state.board_states[i].pips[1-active] - round_state.board_states[i].pips[active]) if isinstance(round_state.board_states[i], BoardState) else 0 for i in range(NUM_BOARDS)])

		for i in range(NUM_BOARDS):
			board_state = round_state.board_states[i]
			board_actions = legal_actions[i]

			if isinstance(board_state, TerminalState) or board_state.settled:
				my_actions[i] = CheckAction()
				continue

			elif AssignAction in legal_actions[i]:
				my_actions[i] = AssignAction(self.card_allocation[i])
				mc = monte_carlo_prob(self.card_allocation[i], [], all_cards_excluding(self.cards))
				for hand_range in branches_from_dealer[0]:
					if mc <= float(hand_range):
						self.players[i].move_down(hand_range)
						print(f'Branching from dealer: {hand_range}')
						break

			elif round_state.street <= 3:
				print(f'-Board {i+1}-')
				pips = board_state.pips[active]
				opp_pips = board_state.pips[1-active]
				pot = board_state.pot + opp_pips + pips
				continue_cost = opp_pips - pips
				count = 0
				while not (self.players[i].is_owner() or self.players[i].at_terminal()):
					if count > 10:
						break
						
					if self.players[i].current_node().get_owner() == 'D':
						mc = self.win_probability(board_state, active)
						for hand_range in branches_from_dealer[1]:
							if mc <= float(hand_range):
								self.players[i].move_down(hand_range)
								print(f'Branching from dealer: {hand_range}')
								break
					else:
						prev = self.players[i].current_node().get_incoming()
						if continue_cost > 0:
							if round_state.street > 0 and prev == 'C':
								self.players[i].move_down('K2')
								print(f'Opp chose branch: K2')
							else:
								branches = []
								for branch in self.players[i].get_branches():
									if 'R' in branch:
										branches.append(branch)
								raise_boundaries = [int((pot - continue_cost) * (2 ** (int(branch.replace('R', '')) - 2.5))) for branch in branches]
								casted_amount = 0
								for k in range(len(raise_boundaries)):
									if continue_cost <= raise_boundaries[k]:
										casted_amount = branches[k].replace('R', '')
										break
								if casted_amount == 0: 
									casted_amount = branches[-1].replace('R', '')

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
					count += 1

				if continue_cost > 2.25 * (pot - continue_cost):
					mc = self.win_probability(board_state, active)
					if (mc > .7 and round_state.street == 0) or (mc > .85 and round_state.street == 3):
						my_actions[i] = CallAction()
						self.players[i].move_down('C')
						print('Swerving branch: C')
					else:
						my_actions[i] = FoldAction()
						self.players[i].move_down('F')
						print('Swerving branch: F')
					continue
				elif not (self.players[i].is_owner() or self.players[i].at_terminal()):
					if CheckAction in board_actions:
						my_actions[i] = CheckAction()
						print('Timed out branch: K')
					else:
						my_actions[i] = CallAction()
						print('Timed out branch: C')
					continue

				branch = self.players[i].choose_branch()
				prev = self.players[i].current_node().get_incoming()
				if 'RR' in branch and CallAction in board_actions:
					my_actions[i] = CallAction()
					self.players[i].move_down('C')
					print('Choosing branch: C')
				elif 'R' in branch and 'RR' not in branch and RaiseAction in board_actions:
					raise_amount = max(BIG_BLIND, min(raise_bounds[1], int(pot * (2 ** (int(branch[1:]) - 3)))))
					raise_bounds[1] -= raise_amount
					my_actions[i] = RaiseAction(raise_amount + opp_pips)
					self.players[i].move_down(branch)
					print('Choosing branch:', branch)
				elif 'C' in branch and CallAction in board_actions:
					my_actions[i] = CallAction()
					self.players[i].move_down(branch)
					print('Choosing branch:', branch)
				elif 'K' in branch and CheckAction in board_actions:
					my_actions[i] = CheckAction()
					self.players[i].move_down(branch)
					print('Choosing branch:', branch)
				elif 'F' in branch and FoldAction in board_actions:
					my_actions[i] = FoldAction()
					self.players[i].move_down(branch)
					print('Choosing branch:', branch)
				elif CheckAction in board_actions:
					my_actions[i] = CheckAction()
					self.players[i].move_down('K')
					print('Defaulting branch: K')
				else:
					my_actions[i] = CallAction()
					self.players[i].move_down('C')
					print('Defaulting branch: C')

			else:				
				pips = board_state.pips[active]
				opp_pips = board_state.pips[1-active]
				continue_cost = opp_pips - pips
				pot = board_state.pot + opp_pips + pips
				pot_odds = float(continue_cost) / (pot + continue_cost)
				win_prob = self.win_probability(board_state, active)

				if continue_cost == 0:
					if win_prob >= .7 and RaiseAction in legal_actions[i] and raise_bounds[1] >= BIG_BLIND:
						if win_prob > 0.96:
							increase = min(raise_bounds[1] - total_cost, int(pot))
						elif win_prob >= 0.9:
							increase = min(raise_bounds[1] - total_cost, int(.75 * pot))
						else:
							increase = min(raise_bounds[1] - total_cost, int(0.5 * pot))
 
						amount = increase
						print(f'Bet/raise board {i + 1} to {amount}.')
						my_actions[i] = RaiseAction(amount)
						raise_bounds[1] -= amount

					else:
						print(f'Check {i + 1}.')
						my_actions[i] = CheckAction()

				else:
					if win_prob > .97 and RaiseAction in legal_actions[i] and raise_bounds[1] >= BIG_BLIND:
						increase = min(raise_bounds[1] - total_cost, int(.5 * pot) + opp_pips)
						amount = increase + opp_pips
						print(f'Reraise board {i + 1} to {amount}.')
						my_actions[i] = RaiseAction(amount)
						raise_bounds[1] -= amount

					elif win_prob - .4 > pot_odds or win_prob > .95 - (.05 * (5 - round_state.street)):
						print(f'Call board {i + 1} w/ {round(pot_odds, 2)} odds.')
						self.when_raised[i].append(round_state.street)
						my_actions[i] = CallAction()
						
					else:
						print(f'Fold board {i + 1}')
						my_actions[i] = FoldAction()

		print()
		return my_actions

if __name__ == '__main__':
	run_bot(Player(), parse_args())
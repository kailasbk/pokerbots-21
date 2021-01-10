from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, AssignAction
from skeleton.states import GameState, TerminalState, RoundState, BoardState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND, NUM_BOARDS
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from cards import *

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

	def win_probability(self, board_state: BoardState, active: int):
		hand = board_state.hands[active]
		deck = board_state.deck

		pool = self.cards
		middle = []

		for card in deck:
			if card != '':
				pool.append(card)
				middle.append(card)

		remaining = createCards(pool)

		return MonteCarloProb(hand, middle, remaining)

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
		self.cards = sortCards(self.cards)
		print("----------BEGIN ROUND {}--CLOCK:{}----------".format(game_state.round_num, game_state.game_clock))

		pass

	def handle_round_over(self, game_state: GameState, round_state: RoundState, active: int):
		'''
		Called when a round ends. Called NUM_ROUNDS times.

		Arguments:
		game_state: the GameState object.
		terminal_state: the TerminalState object.
		active: your player's index.

		Returns:
		Nothing.
		'''
		print("----------END ROUND {}----CLOCK:{}----------".format(game_state.round_num, game_state.game_clock))
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
		for i in range(NUM_BOARDS):
			if AssignAction in legal_actions[i]:
				cards = [self.cards[2*i], self.cards[2*i+1]]
				my_actions[i] = AssignAction(cards)
			else:
				board_state = round_state.board_states[i]
				if isinstance(board_state, TerminalState):
					my_actions[i] = CheckAction()
					continue
				continue_cost = board_state.pips[1-active] - board_state.pips[active]
				pot = board_state.pot
				potOdds = float(continue_cost) / (pot + continue_cost)
				winProb = self.win_probability(board_state, active)
				
				# if they haven't raised and we can raise
				if winProb >= .8 and RaiseAction in legal_actions[i] and stack != 0:
					increase = (3 * BIG_BLIND)
					amount = board_state.pips[1-active] + increase
					# if can bet normally
					if stack > 3 * BIG_BLIND + continue_cost and board_state.pips[active] < 30:
						print('Betting/raising on board {} to {}.'.format(i + 1, amount))
						my_actions[i] = RaiseAction(amount)
						stack -= amount
					# otherwise (don't do all in rn)
					else:
						if CallAction in legal_actions[i]:
							print('Calling on board {}.'.format(i + 1))
							my_actions[i] = CallAction()
						elif CheckAction in legal_actions[i]:
							print('Checking on board {}.'.format(i + 1))
							my_actions[i] = CheckAction()
				# if opponent just raised (call and fold, maybe raise, are legal)
				elif CallAction in legal_actions[i]:
					# check on the board
					if (winProb > potOdds):
						print('Calling on board {}.'.format(i + 1))
						my_actions[i] = CallAction()
					else:
						print('Folding on board {}.'.format(i + 1))
						my_actions[i] = FoldAction()
				# if its not worth raising, just check
				elif CheckAction in legal_actions[i]:
					# else check on the board
					print('Checking on board {}.'.format(i + 1))
					my_actions[i] = CheckAction()
		return my_actions

if __name__ == '__main__':
	run_bot(Player(), parse_args())
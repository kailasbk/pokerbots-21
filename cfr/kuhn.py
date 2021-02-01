from nodes import Node
from player import Player
import random

c = open('log.csv', 'w')
c.write('round,queen call,jack bet\n')

gametree = Node('D')
gametree.create_children(['king', 'queen', 'jack'], 'P1')
for branch in gametree.get_branches():
    # make the "same" tree for each card
    first_turn = gametree.get_child(branch)
    first_turn.create_children(['K1', 'R1'], 'P2')
    second_turn_check = first_turn.get_child('K1')
    second_turn_check.create_child('K2,E', 'D')
    second_turn_check.create_child('R1', 'P1')
    second_turn_raise = first_turn.get_child('R1')
    second_turn_raise.create_children(['C,E', 'F,E'], 'D')
    third_turn = second_turn_check.get_child('R1')
    third_turn.create_children(['C,E', 'F,E'], 'D')

class Game:
    """
    Facilitates a game of poker
    """
    def __init__(self, tree: Node):
        names = ['P1', 'P2']
        cards = ['jack', 'queen', 'king']
        self.hands = random.sample(cards, 2)
        self.players = [Player(names[i], tree) for i in range(2)]
        self.history = []
        self.last_turn = self.players[1]

    def is_finished(self) -> bool:
        assert self.players[0].at_terminal() == self.players[1].at_terminal()
        return self.players[0].at_terminal()

    def move_up(self):
        for player in self.players:
            player.move_up()
        
        self.history.pop()

    def move_down(self, branch):
        for player in self.players:
            player.move_down(branch)
        
        self.history.append(branch)

    def get_players(self) -> list:
        return self.players

    def get_history(self) -> list:
        return self.history

    def take_turn(self):
        branch = ''
        for player in self.players:
            if player.is_owner():
                self.last_turn = player
                branch = player.choose_branch()
                #print(str(player) + ' chooses ' + branch)
                break

        if branch != '':
            self.move_down(branch)

        else:
            self.history.append('D')
            for i in range(len(self.players)):
                self.players[i].move_down(self.hands[i])

    def play(self) -> str:
        while not self.is_finished():
            self.take_turn()
        
        total = 2
        raise_amount = 0

        for event in self.history:
            if 'R' in event:
                raise_amount = int(event[1:])
            elif 'C' in event:
                total += 2 * raise_amount
                raise_amount = 0

        if 'F' in self.history[-1]:
            return f'{self.last_turn} -{int(total / 2)}'
        else:
            vals = {'king': 3, 'queen': 2, 'jack': 1}
            if vals[self.hands[0]] > vals[self.hands[1]]:
                return f'P1 {int(total / 2)}'
            elif vals[self.hands[0]] < vals[self.hands[1]]:
                return f'P2 {int(total / 2)}'
            else:
                return 'SP 0'

input(f'The game tree has {Node.number_of_nodes()} nodes. Press ENTER to proceeed.')
#print(h.heap())

def compute_regrets(root_node: list, value: int):
    move_taken = player.get_history()[-1]
    game.move_up()
    while player.current_node() != root_node:
        if player.is_owner():
            node = player.current_node()
            for branch in node.get_branches():
                new_value = 0
                if branch != move_taken:
                    game.move_down(branch)
                    new_result = game.play()
                    if new_result[0:2] == str(player):
                        new_value = int(new_result[3:])
                    else:
                        new_value = -int(new_result[3:])
                    node.add_regret(branch, new_value - value)
                    print(f'updating regrets for node #{node.get_id()}')
                    compute_regrets(node, new_value)
                while player.current_node() != node:
                    game.move_up()

        move_taken = player.get_history()[-1]
        game.move_up()

ITERS = 100000
queen_sum = 0
jack_sum = 0
updates = 0
for k in range(ITERS):
    game = Game(gametree)
    player = game.get_players()[k % 2]
    result = game.play()
    value = 0

    if result[0:2] == str(player):
        value = int(result[3:])
    else:
        value = -int(result[3:])

    compute_regrets(gametree, value)

    if k > 100:
        queen_strat = Node.all_nodes[13].get_strategy()
        queen_call = queen_strat['C,E']
        queen_sum += queen_call * (1 + float(5 * k/ITERS))
        jack_strat = Node.all_nodes[20].get_strategy()
        jack_bet = jack_strat['R1']
        jack_sum += jack_bet * (1 + float(5 * k/ITERS))
        updates += (1 + float(5 * k/ITERS))
        if k % 1000 == 0:
            try:
                c.write(f'{k + 1},{queen_sum / updates},{jack_sum / updates}\n')
            except:
                pass
    print(f'completed iteration {k + 1}')

print(queen_sum / updates, jack_sum / updates)

f = open('regrets.txt', 'w')

for node in Node.get_all_nodes():
    regrets = node.get_regrets()
    if regrets != {}:
        f.write(f'{node.get_id()},{node.get_owner()},{regrets},{[node.get_child(branch).get_id() for branch in node.get_branches()]} \n')
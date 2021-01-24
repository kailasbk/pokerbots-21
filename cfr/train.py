from nodes import Node
from player import *
from tree import *
from game import *
from guppy import hpy

h = hpy()

gametree = create_game_tree()
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
                    node.add_regret(branch, int((1 + (k/ITERS)) * (new_value - value)))
                    print(f'updating regrets for node #{node.get_id()}')
                    compute_regrets(node, new_value)
                while player.current_node() != node:
                    print(player.current_node().get_id())
                    game.move_up()

        move_taken = player.get_history()[-1]
        game.move_up()

ITERS = 10000
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
    
    print(f'completed iteration {k + 1}')

f = open('regrets.txt', 'w')

for node in Node.get_all_nodes():
    regrets = node.get_regrets()
    if regrets != {}:
        f.write(f'{node.get_id()},{node.get_owner()},{regrets},{[node.get_child(branch).get_id() for branch in node.get_branches()]} \n')
from nodes import Node
from player import *
from tree import *
from game import *
from guppy import hpy

h = hpy()

gametree = create_game_tree()
input(f'The game tree has {Node.number_of_nodes()} nodes. Press ENTER to proceeed.')
#print(h.heap())

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

    while not player.at_start():
        move_taken = player.get_history()[-1]
        while not (player.at_start() or player.is_owner()):
            move_taken = player.get_history()[-1]
            game.move_up()
        if player.is_owner():
            node = player.current_node()
            print(node)
            for branch in node.get_branches():
                new_value = 0
                if branch != move_taken:
                    game.move_down(branch)
                    new_result = game.play()
                    if result[0:2] == str(player):
                        new_value = int(result[3:])
                    else:
                        new_value = -int(result[3:])
                node.add_regret(branch, new_value - value)
                while player.current_node() != node:
                    game.move_up()
            game.move_up()
    
    print(f'completed iteration {k + 1}')

f = open('regrets.txt', 'w')

for node in Node.get_all_nodes():
    regrets = node.get_regrets()
    if regrets != {}:
        f.write(str(regrets) + '\n')
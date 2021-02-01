from .nodes import Node
from .player import *
from .tree import *
from .game import *
from guppy import hpy
import json

h = hpy()

gametree = create_game_tree()
input(f'The game tree has {Node.number_of_nodes()} nodes. Press ENTER to proceeed.')
#print(h.heap())

def compute_regrets(player: Player, root_node: list, value: int):
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
                    compute_regrets(player, node, new_value)
                while player.current_node() != node:
                    game.move_up()

        move_taken = player.get_history()[-1]
        game.move_up()

ITERS = 1000000
strategy_sum = [{}] * Node.number_of_nodes()

for node in Node.all_nodes:
    if not node.is_terminal():
        strategy_sum[node.get_id() - 1] = node.get_regrets().copy()

for k in range(ITERS):
    game = Game(gametree)
    player = game.get_players()[k % 2]
    result = game.play()
    value = 0

    if result[0:2] == str(player):
        value = int(result[3:])
    else:
        value = -int(result[3:])

    # compute regret for every decision
    compute_regrets(player, gametree, value)

    # adjust average strategy
    weight = 1 + float(k/ITERS)
    for node in Node.all_nodes:
        if node.get_owner() == str(player) and not node.is_terminal():
            strategy = strategy_sum[node.get_id() - 1]
            new_strategy = node.get_strategy()
            for branch in strategy:
                strategy_sum[node.get_id() - 1][branch] += weight * new_strategy[branch]
    
    if (k + 1) * 10 % ITERS == 0:
        strategy_copy = strategy_sum.copy()
        for strat in strategy_copy:
            if strat != {}:
                sum = 0
                for branch in strat:
                    sum += strat[branch]
                
                if sum != 0:
                    for branch in strat:
                        strat[branch] /= sum

        f = open(f'strats/strategy{k+1}.json', 'w')
        json.dump(strategy_sum, f)
        f.close()

        regret_snapshot = []
        for node in Node.all_nodes:
            regret_snapshot.append(node.get_regrets())

        f = open(f'strats/regrets{k+1}.json', 'w')
        json.dump(regret_snapshot, f)
        f.close()
            
    print(f'completed iteration {k + 1}')
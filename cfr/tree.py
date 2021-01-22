import random
from nodes import *

branches_after_dealer = ['check 1', 'raise 6']
branches_from_check = ['raise 6']
ends_round = ['check 2', 'call']
branches_from_dealer = ['.2', '.4', '.6', '.8', '1.0']
dealer_turns = ['hand', 'flop', 'turn', 'river', 'end']

def expand_game_tree(start: Node, round: int):
    """
    Takes a starting node and expandes the game tree on its childen.
    Will be changed later using get_incoming() and create children for a node, which makes more sense
    """
    for branch in start.get_branches():
        if 'end' in branch:
            continue
        child: Node = start.get_child(branch)
        opp_owner = 'BB' if child.get_owner() == 'SB' else 'SB'
        if start.get_owner() == 'D':
            if round == 1:
                child.create_child(f'call => {dealer_turns[round + 1]}', 'D')
                child.create_child('fold => end', 'D')
                call_child = child.get_child(f'call => {dealer_turns[round + 1]}')
                call_child.create_children(branches_from_check, 'SB')
                expand_game_tree(call_child, round)
    
            else:
                child.create_children(branches_after_dealer, 'SB') # add more raises later
                expand_game_tree(child, round)

        elif child.get_owner() == 'D':
            child.create_children(branches_from_dealer, 'BB')
            expand_game_tree(child, round + 1)

        elif branch == 'check 1':
            child.create_child(f'check 2,{dealer_turns[round + 1]}', 'D')
            child.create_children(branches_from_check, opp_owner)
            expand_game_tree(child, round)

        elif 'raise' in branch:
            child.create_child(f'call,{dealer_turns[round + 1]}', 'D')
            child.create_child('fold,end', 'D')
            expand_game_tree(child, round)

def create_game_tree():
    start = Node('D')
    start.create_children(branches_from_dealer, 'SB')
    expand_game_tree(start, 1)

    return start

start = create_game_tree()
print(Node.number_of_nodes())
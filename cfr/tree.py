from .nodes import *

raise_branches = ['R1', 'R2', 'R3', 'R4', 'R5'] # Raise
reraise_branches = ['RR1', 'RR2', 'RR3', 'RR4'] #ReRaise
ends_round = ['K2', 'C'] # checK, Call
branches_from_dealer = [['.5', '.7', '.9'], ['.2', '.4', '.6', '.7', '.8', '.9', '1.0']]
dealer_turns = ['H', 'L', 'E'] # Hand, fLop, Turn, riVer, End

def expand_game_tree(start: Node, round: int):
    """
    Takes a starting node and expandes the game tree on its childen.
    """
    incoming_branch = start.get_incoming()

    if 'E' in incoming_branch:
        return

    opp_owner = 'BB' if start.get_owner() == 'SB' else 'SB'

    if start.get_owner() == 'D':
        player = 'SB' if round == 0 else 'BB'
        start.create_children(branches_from_dealer[round], player)
        round += 1

    elif start.get_parent().get_owner() == 'D':
        if round == 1:
            start.create_child('C', 'BB')
            start.create_child('F,E', 'D')
            start.create_children(reraise_branches, 'BB')
            call_child = start.get_child('C')
            call_child.create_child('K2,L', 'D')
            call_child.create_children(raise_branches, 'SB')
        else:
            start.create_child('K1', 'SB')
            start.create_children(raise_branches, 'SB')
    
    elif 'RR' in incoming_branch:
        start.create_child(f'C,{dealer_turns[round]}', 'D')
        start.create_child('F,E', 'D')

    elif 'R' in incoming_branch:
        start.create_child(f'C,{dealer_turns[round]}', 'D')
        start.create_child('F,E', 'D')
        start.create_children(reraise_branches, opp_owner)

    elif 'K1' == incoming_branch:
        start.create_child(f'K2,{dealer_turns[round]}', 'D')
        start.create_children(raise_branches, opp_owner)

    for branch in start.get_branches():
        expand_game_tree(start.get_child(branch), round)

def create_game_tree():
    start = Node('D')
    expand_game_tree(start, 0)

    return start
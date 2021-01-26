from .nodes import *
from .tree import *
import random

class Player:
    """
    A player which can traverse a game tree
    """
    def __init__(self, name, start, hand = ['Ah', 'Ad']):
        self.name: str = name 
        self.start: Node = start
        self.current: Node = self.start
        self.history: list = ['start']
        self.stack = 200
        self.hand = hand

    def __str__(self):
        return self.name

    def get_branches(self):
        return self.current.get_branches()

    def get_hand(self):
        return self.hand

    def set_hand(self, hand):
        self.hand = hand

    def get_history(self):
        return self.history

    def at_start(self) -> bool:
        return self.current.get_incoming() == ''

    def at_terminal(self) -> bool:
        return self.current.is_terminal()

    def current_node(self) -> Node:
        return self.current

    def choose_branch(self) -> str:
        if self.at_terminal():
            return ''

        strategy = self.current.get_strategy()
        
        return random.choices(list(strategy.keys()), list(strategy.values()))[0]

    def move_up(self):
        parent = self.current.get_parent()
        if parent != None:
            self.current = parent
            self.history.pop()

    def move_down(self, branch):
        if branch in self.current.get_branches():
            self.prev_branch = branch
            self.current = self.current.get_child(branch)
            self.history.append(branch)
        
        else:
            for branch_candidate in self.current.get_branches():
                if branch in branch_candidate:
                    self.prev_branch = branch_candidate
                    self.current = self.current.get_child(branch_candidate)
                    self.history.append(branch_candidate)
                    break

    def is_owner(self) -> bool:
        return self.current.get_owner() == self.name
    
    def test_tree(self):
        while not self.at_terminal():
            self.move_down(self.choose_branch())
        
        print(self.history)
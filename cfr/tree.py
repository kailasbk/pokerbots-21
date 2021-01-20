import random
from nodes import Node

class Tree:
    """
    A tree of nodes that represents a poker game
    """
    def __init__(self):
        self.start = Node('D')
        self.current = self.start
        self.prev_branch = ''

    def get_branches(self):
        return self.current.get_branches()

    def at_terminal(self):
        return self.current.is_terminal()

    def choose_branch(self) -> str:
        if self.at_terminal():
            return ''

        regrets = self.current.get_regrets()
        sum = 0
        for regret in regrets.items():
            sum += regret
        
        if sum == 0:
            return random.choice(regrets.keys())
        else:
            num = random.randint(1, sum)

            for key in regrets:
                num -= regrets[key]
                if num <= 0:
                    return key

    def move_up(self):
        parent = self.current.get_parent()
        if parent != None:
            self.current = parent

    def move_down(self, branch):
        if branch in self.current.get_branches():
            self.prev_branch = branch
            self.current = self.current.get_child(branch)

    def expand_tree(self, start: Node, prev: str = 'R'):
        """
        Create the game tree using a recursive algorithm
        """
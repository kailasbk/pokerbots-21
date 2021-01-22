from nodes import *
from tree import *
from guppy import hpy

h = hpy()

class Player:
    """
    A player which can traverse a game tree
    """
    def __init__(self, name, start):
        self.name = name 
        self.start = start
        self.current = self.start
        self.history = ['start']

    def __str__(self):
        return f'I am currently as node #{self.current.get_id()}'

    def get_branches(self):
        return self.current.get_branches()

    def at_terminal(self):
        return self.current.is_terminal()

    def choose_branch(self) -> str:
        if self.at_terminal():
            return ''

        regrets = self.current.get_regrets()
        sum = 0
        for regret in regrets.values():
            sum += regret
        
        if sum == 0:
            return random.choice(list(regrets.keys()))
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
            self.history.pop()

    def move_down(self, branch):
        if branch in self.current.get_branches():
            self.prev_branch = branch
            self.current = self.current.get_child(branch)
            self.history.append(branch)

    def owns_node(self):
        return self.current.get_owner == self.name
    
    def test_tree(self):
        while not self.at_terminal():
            self.move_down(self.choose_branch())
        
        print(self.history)

start = create_game_tree()
player = Player('SB', start)
player.test_tree()
print(Node.number_of_nodes())
print(h.heap())
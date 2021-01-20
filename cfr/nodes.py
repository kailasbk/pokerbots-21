class Node:
    """
    A Node in the gametree
    """
    id = 1

    def __init__(self, owner: str = '', parent = None):
        """
        Creates the Node
        """
        self.id = Node.id
        Node.id += 1
        self.parent = parent
        self.owner = owner
        self.regrets = {}
        self.children = {}

        pass

    def __str__(self) -> str:
        string = f'--node {self.id}-- \n'
        if (self.parent != None):
            string += f'parent: {self.parent.get_id()} \n'
        string += f'owner: {self.owner} \n'
        string += f'regrets: {self.regrets} \n'
        string += f'children: '
        for key in self.children:
            string += f'{key}: {self.children[key].get_id()}, '
        return string

    def is_terminal(self) -> bool:
        return len(self.children) == 0

    def get_id(self) -> int:
        return self.id

    def get_owner(self) -> str:
        return self.owner
    
    def get_parent(self):
        return self.parent

    def get_child(self, branch):
        return self.children[branch]

    def get_branches(self) -> dict:
        return self.children.keys()

    def set_owner(self, new):
        self.owner = new

    def set_parent(self, parent):
        self.parent = parent
    
    def set_children(self, children: dict):
        self.children = children
        self.reset_regrets()

    def append(self, branch, child):
        child.set_parent(self)
        self.children[branch] = child
        self.regrets[branch] = 0

    def create_children(self, branches, owner):
        for branch in branches:
            self.append(branch, Node(owner))

    def get_regrets(self):
        return self.regrets

    def add_regret(self, branch, amount):
        if branch in self.get_branches():
            self.regrets[branch] += amount
            if self.regrets[branch] < 0:
                self.regrets[branch] = 0

    def reset_regrets(self):
        self.regrets = dict.fromkeys(self.children.keys(), 0)
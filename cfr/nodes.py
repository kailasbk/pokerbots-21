class Node:
    """
    A Node in the gametree
    """
    id = 1
    all_nodes = []

    def __init__(self, owner: str = '', incoming = '', parent = None):
        """
        Creates the Node
        """
        self.id = Node.id
        Node.id += 1
        self.parent = parent
        self.incoming = incoming
        self.owner = owner
        self.branches = {}
        Node.all_nodes.append(self)

        pass

    def __str__(self) -> str:
        string = f'--node #{self.id}-- \n'
        if (self.parent != None):
            string += f'parent: #{self.parent.get_id()} => {self.incoming}\n'
        string += f'owner: {self.owner} \n'
        string += f'regrets: {self.get_regrets()} \n'
        string += f'branches => children: '
        for key in self.branches:
            string += f'{key} => #{self.branches[key][0].get_id()}, '
        return string

    def get_node(id):
        if len(Node.all_nodes) >= id:
            return Node.all_nodes[id - 1]

    def get_all_nodes() -> list:
        return Node.all_nodes

    def number_of_nodes():
        return len(Node.all_nodes)

    def is_terminal(self) -> bool:
        return len(self.branches) == 0

    def get_id(self) -> int:
        return self.id

    def get_owner(self) -> str:
        return self.owner
    
    def get_parent(self):
        return self.parent

    def get_incoming(self):
        return self.incoming

    def set_incoming(self, incoming):
        self.incoming = incoming

    def get_child(self, branch):
        return self.branches[branch][0]

    def get_branches(self):
        return self.branches.keys()

    def set_owner(self, new):
        self.owner = new

    def set_parent(self, parent):
        self.parent = parent

    def append(self, branch, child):
        child.set_parent(self)
        child.set_incoming(branch)
        self.branches[branch] = (child, 0)

    def create_child(self, branch, owner):
        self.append(branch, Node(owner, branch))

    def create_children(self, branches, owner):
        for branch in branches:
            self.create_child(branch, owner)

    def get_regrets(self) -> dict:
        d = {}
        for branch in self.branches:
            d[branch] = self.branches[branch][1]
        return d

    def get_strategy(self) -> dict:
        d = {}
        sum = 0
        length = len(self.branches)
        for branch in self.branches.values():
            if branch[1] > 0:
                sum += branch[1]
        
        for branch in self.branches:
            if sum != 0:
                if self.branches[branch][1] > 0:
                    d[branch] = self.branches[branch][1] / sum
                else:
                    d[branch] = 0
            else:
                d[branch] = 1 / length

        return d

    def set_strategy(self, strat):
        for branch in strat:
            self.branches[branch] = (self.branches[branch][0], int(strat[branch] * 20))

    def set_regrets(self, regrets):
        for branch in regrets:
            self.branches[branch] = (self.branches[branch][0], regrets[branch])

    def add_regret(self, branch, amount):
        if branch in self.branches:
            new_amount = self.branches[branch][1] + amount
            if new_amount < 0:
                new_amount = 0
            self.branches[branch] = (self.branches[branch][0], new_amount)
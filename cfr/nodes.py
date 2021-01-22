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
        self.regrets = {}
        self.children = {}
        Node.all_nodes.append(self)

        pass

    def __str__(self) -> str:
        string = f'--node #{self.id}-- \n'
        if (self.parent != None):
            string += f'parent: #{self.parent.get_id()} => {self.incoming}\n'
        string += f'owner: {self.owner} \n'
        string += f'regrets: {self.regrets} \n'
        string += f'branches => children: '
        for key in self.children:
            string += f'{key} => #{self.children[key].get_id()}, '
        return string

    def get_node(id):
        if len(Node.all_nodes) >= id:
            return Node.all_nodes[id - 1]

    def get_all_nodes() -> list:
        return Node.all_nodes

    def number_of_nodes():
        return len(Node.all_nodes)

    def is_terminal(self) -> bool:
        return len(self.children) == 0

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
        return self.children[branch]

    def get_branches(self):
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
        child.set_incoming(branch)
        self.children[branch] = child
        self.regrets[branch] = 0

    def create_child(self, branch, owner):
        self.append(branch, Node(owner, branch))

    def create_children(self, branches, owner):
        for branch in branches:
            self.create_child(branch, owner)

    def get_regrets(self):
        return self.regrets

    def set_regrets(self, regrets):
        for key in regrets:
            self.regrets[key] = regrets[key]

    def add_regret(self, branch, amount):
        if branch in self.get_branches():
            self.regrets[branch] += amount
            if self.regrets[branch] < 0:
                self.regrets[branch] = 0

    def reset_regrets(self):
        self.regrets = dict.fromkeys(self.children.keys(), 0)
class Node:
    """
    Represents a node in the blockchain network.
    """

    nodes = {}  # class variable to hold all nodes

    def __init__(self, id, name, privilege):
        """
        Initializes a new instance of the Node class.

        Args:
            id (int): The unique identifier of the node.
            name (str): The name of the node.
            privilege (float): The amount of privileges held by the node.
        """
        self.id = id
        self.name = name
        self.privilege = privilege
        Node.nodes[id] = self  # add the node to the class variable

    def __repr__(self):
        return f"{self.id}: {self.name} -> {self.privilege}"

    @classmethod
    def add_node(cls, id, name):
        """
        Adds a new node to the class variable.

        Args:
            id (int): The unique identifier of the node.
            name (str): The name of the node.
            privilege (float): The amount of privileges held by the node.
        """
        node = cls(id, name, 0)
        cls.nodes[id] = node

    def update(self, task_type, amount):
        """
        Updates the privilege amount of the node based on the task type and privilege amount provided.

        Args:
            task_type (str): The type of task performed (e.g. reward, punishment).
            amount (float): The amount of privileges earned or spent for the task.
        """
        if task_type == 'reward':
            self.privilege += amount
        elif task_type == 'punishment':
            if self.privilege < amount:
                print (f"{self.name} does not have sufficient privileges.")
                #raise ValueError("Insufficient privileges.")
                self.privilege = 0
            else:
                self.privilege -= amount
        elif task_type == 'common_landmark':
            self.privilege += amount
        elif task_type == 'add_panoramic':
            self.privilege += amount
        elif task_type == 'start':
            self.privilege = amount
        elif task_type == 'new_node':
            self.privilege += amount
        else:
            print ("Invalid task type.")
            #raise ValueError("Invalid task type.")
    
    @classmethod
    def get_node_by_name(cls, name):
        """
        Returns the node with the specified name.

        Args:
            name (str): The name of the node to get.

        Returns:
            Node: The node with the specified name.
        """
        
        for node in cls.nodes.values():
            if node.name == name:
                #print (node)
                return node
            #print(f"A node with name {name} is not found.")
        #raise ValueError(f"A node with name {name} is not found.")

    @classmethod
    def get_node_by_id(cls, id):
        """
        Returns the node with the specified id.

        Args:
            id (int): The id of the node to get.

        Returns:
            Node: The node with the specified id.
        """
        node = cls.nodes.get(id)
        if not node:
            print (f"A node with id {id} is not found.")
        else:
            #print(node)
            return node
            #raise ValueError(f"A node with id {id} is not found.")
        

    @classmethod
    def get_all_nodes(cls):
        """
        Returns a list of dictionaries, where each dictionary contains the details
        of a node (i.e., id, name, and privilege).
        """
        all_nodes = []
        for node_id, node_obj in cls.nodes.items():
            node_dict = {
                'id': node_id,
                'name': node_obj.name,
                'privilege': node_obj.privilege
            }
            all_nodes.append(node_dict)
        return all_nodes

from transaction import Transaction
from block import Block
from node import Node
import hashlib
import random
from datetime import datetime
import time
import csv


class Blockchain:
    """
    Represents a blockchain.
    """
    def __init__(self,consensus):
        """
        Initializes a new instance of the Blockchain class.
        Argument:
        Consensus type:
            proof of ? = "poc"
            Proof of Work " "pow" 
            Proof of Stake : "pos"
            Delegated Proof of Stake : "dpos"
            Proof of Authority : "poa"
        """
        self.consensus = consensus
        self.chain = []
        self.validators = {}
        self.pending_transactions = []
        self.nodes = {}
        self.nonce = {}
        # Create the genesis block
        self.create_genesis_block()
        self.blockstimes={}
        self.navigability=[]

    def update(self, robot, task_type, amount):
        """
        Updates the privilege amount of the node based on the task type and privilege amount provided.

        Args:
            task_type (str): The type of task performed (e.g. reward, punishment).
            amount (float): The amount of privileges earned or spent for the task.
        """
        for node in self.nodes:
            loc=node["id"]
            if node["name"] == robot:
                if task_type == 'reward':
                    node["privilege"] += amount
                elif task_type == 'punishment':
                    if node["privilege"] < amount:
                        #raise ValueError("Insufficient privileges.")
                        node["privilege"] = 0
                    else:
                        node["privilege"] -= amount
                elif task_type == 'common_landmark':
                    node["privilege"] += amount
                elif task_type == 'add_panoramic':
                    node["privilege"] += amount
                elif task_type == 'start':
                    node["privilege"] = amount
                elif task_type == 'new_node':
                    node["privilege"] += amount
                else:
                    print ("Invalid task type.")
                    #raise ValueError("Invalid task type.")  
                    
        if task_type == 'start':
           num_nodes = len(self.nodes)
           self.navigability = [[0] * num_nodes for _ in range(num_nodes)] 
                    
    def create_genesis_block(self):
        """
        Creates the genesis block and adds it to the blockchain.
        """
        # Create an initial transaction for the genesis block
        genesis_transaction = Transaction(-1, "Sender",["Panorama"], "Partner", ["common landmarks"],-1)
        # Create the genesis block
        genesis_block = Block(-1, [genesis_transaction],"Navigability" ,"Previous hash", "Miner")
        # Add the genesis block to the chain
        self.chain.append(genesis_block)

    def add_transaction(self, transaction):
        """
        Adds a transaction to the list of pending transactions.
        Args:
        transaction (Transaction): The transaction to add.
        """
        self.pending_transactions.append(transaction)
        
        
    def generate_block(self):
        """
        """
        #Calculate the time difference between last block and current time in second
        #based on block
        Success=0
        fid=self.chain[-1].id
        Gen_Block = None
        delta = time.mktime(time.strptime(time.ctime()))-time.mktime(time.strptime(self.latest_block().timestamp))
           
        if len(self.pending_transactions) != 0 and (len(self.pending_transactions) >= len(self.nodes) or delta > 40):
            #start_time = time.ctime()
            start_time = datetime.now()
            if self.consensus == "pow" :
                Gen_Block = self.pow_mine()        
            elif self.consensus == "pos" :
                Gen_Block = self.pos_mine()
            elif self.consensus == "dpos" :
                Gen_Block = self.dpos_mine()                        
            elif self.consensus == "poa" :
                Gen_Block = self.poa_mine()
            elif self.consensus == "poc" :
                Gen_Block = self.poc_mine()
            Success=self.chain[-1].id-fid
            if Success == 1:
                print(F"The Block number {Gen_Block} was generated based on {self.consensus}")
                #end_time = time.ctime()
                end_time = datetime.now()
                duration = end_time - start_time
                self.blockstimes[self.chain[-1].id] = [start_time,end_time,duration]
        Success=self.chain[-1].id-fid 
        if Success != 1 :
            print(F"The Block is not generated yet")
            print(F"Number of pending transactions ({self.consensus}): {len(self.pending_transactions)}")
            return Success,[]
        return Success,Gen_Block
        
    def select_miner(self):
        """
        Selects a miner randomly from the top 20% validators based on their stake.

        Returns:
        str: The selected validator.
        """
        # List of validators with their stakes.
        self.validators = {node['name']: node['privilege'] for node in self.nodes}        
        # Sort the validators by stake (descending order)
        sorted_validators = sorted(self.validators.items(), key=lambda x: x[1], reverse=True)        
        # Get the top 20 % validators based on their stake or at least 2 of them
        top_validators = sorted_validators[:max(int(len(sorted_validators) * 0.2) , 2)]
        # Randomly select one of the top validators
        miner = random.choice(top_validators)
        # Return the address of the selected validator
        return miner
    
    def select_miner_poc(self):
        """
        Create a navigability matrix and Select the best miner based on it.

        Returns:
        str: The selected validator.
        """
        num_nodes = len(self.nodes)
        self.navigability = [[0] * num_nodes for _ in range(num_nodes)]
        # List of validators with their stakes.
        self.validators = {node['name']: node['privilege'] for node in self.nodes}
        print("Nodes: ",self.validators)
        total_token = sum(self.validators.values())
        # self.weights = {node: token / total_token  for node, token in self.validators.items()}
        validator_keys = list(self.validators.keys())
        for ref_node, token in self.validators.items():
            ref_index = validator_keys.index(ref_node)
            stack_weight = token / total_token

            for par_node in self.validators.keys():
                if ref_node != par_node:
                    par_index = validator_keys.index(par_node)
                    landmarks_weight = self.landmarks_weight(ref_node, par_node)
                    impact_factor = self.impact_factor(ref_node, par_node)
                    self.navigability[ref_index][par_index] = stack_weight * landmarks_weight * impact_factor
        print("Navigability: ",self.navigability)
        max_nav = float('-inf')
        max_indices = (0,0)
        for i in range(num_nodes):
           for j in range(num_nodes):
              if self.navigability[i][j] > max_nav:
                max_nav = self.navigability[i][j]
                max_indices = (i,j)
        selected_validator = random.choice([validator_keys[max_indices[0]], validator_keys[max_indices[1]]])              
        return selected_validator


    def pow_mine(self):
        # Get the previous block in the chain
        previous_block = self.latest_block()                
        # Get the id of the new block
        id = previous_block.id + 1
        
        # (#temp) Get the miner of the current block regarding to max token each one has
        miner=random.choice([node for node in self.nodes])
        
        # Define the Difficulty level --> the number of leading Zero required in hash
        difficulty = self.adjust_difficulty()
        prefix='0' * difficulty
        
        while True : 
        # Calculates the hash of the block     
            block_string = f'{id}{self.pending_transactions}{time.ctime()}{previous_block.hash}{miner}'
            hash_value = hashlib.sha256(block_string.encode()).hexdigest() 
            #print("Hash Value : ",hash_value)
            # checkfor difficulty
            if hash_value.startswith(prefix):
                # Mine the new block
                # Create a new block with the pending transactions 
                new_block = Block(id, self.pending_transactions, self.navigability, previous_block.hash,miner)                              
                # Check the validation before add the block
                last_valid_block = self.chain[-1]
                if new_block.previous_hash == last_valid_block.hash:
                    # Add the new block to the chain
                    self.chain.append(new_block)
                    # Clear the list of pending transactions
                    self.pending_transactions = []
                    return new_block
                else: 
                    print (f"Something goes wrong with the {selected_miner[0]}, it generated invalid block")               
                    self.pow_mine()
                    return []
     
    def adjust_difficulty(self):
        return 1
          
    
    def pos_mine(self):
        """
        Mines a new block by creating a new block from the pending transactions and adding it to the chain.
        Consensus : PoS
        """

        # Get the previous block in the chain
        previous_block = self.latest_block()        
        # Get the miner of the current block regarding to max token each one has
        selected_miner = self.select_miner()        
        # Get the id of the new block
        id = previous_block.id + 1        
        # Mine the new block
        self.navigability = []
        # Create a new block with the pending transactions 
        new_block = Block(id, self.pending_transactions, self.navigability, previous_block.hash, selected_miner)                              
        # Check the validation before add the block
        last_valid_block = self.chain[-1]
        if new_block.previous_hash == last_valid_block.hash:
            # Add the new block to the chain
            self.chain.append(new_block)
            # Clear the list of pending transactions
            self.pending_transactions = []
            return new_block
        else:
            self.update(selected_miner,'punishment', 40) 
            print (f"Something goes wrong with the {selected_miner[0]}, it generated invalid block")               
            self.pos_mine()
            return []
        
        
    def dpos_mine(self):
        """
        Mines a new block by creating a new block from the pending transactions and adding it to the chain.
        Consensus : DPoS
        """
        # Get the previous block in the chain
        previous_block = self.latest_block()
        # Get the id of the new block
        id = previous_block.id + 1
        # Get the miner of the current block regarding to the max vote
        max_votes=max(node['privilege'] for node in self.nodes)
        miner=random.choice([node for node in self.nodes if node['privilege'] == max_votes])                              
        # Mine the new block
        self.navigability = []
        # Create a new block with the pending transactions 
        new_block = Block(id, self.pending_transactions, self.navigability, previous_block.hash,miner)
        # Add the new block to the chain
        # Check the validation before add the block
        last_valid_block = self.chain[-1]
        if new_block.previous_hash == last_valid_block.hash:
            # Add the new block to the chain
            self.chain.append(new_block)
            # Clear the list of pending transactions
            self.pending_transactions = []
            for node in self.nodes:
                self.update(node,"start", 1)
                return new_block
        else:
            self.update(miner,'punishment', 40)
            print (f"Something goes wrong with the {miner}, it generated invalid block")               
            self.dpos_mine()
            return []
        

    def poa_mine(self):
        """
        Mines a new block by creating a new block from the pending transactions and adding it to the chain.
        Consensus : PoA
        """
        # Get the previous block in the chain
        previous_block = self.latest_block()
        # Get the id of the new block
        id = previous_block.id + 1
        # Get the miner of the current block regarding to the list 
        miner=random.choice([node for node in self.nodes if node['privilege'] == 1]) 
        # Mine the new block
        self.navigability = []
        # Create a new block with the pending transactions 
        new_block = Block(id, self.pending_transactions, self.navigability, previous_block.hash,miner)
        # Check the validation before add the block
        last_valid_block = self.chain[-1]
        if new_block.previous_hash == last_valid_block.hash:
            # Add the new block to the chain
            self.chain.append(new_block)
            # Clear the list of pending transactions
            self.pending_transactions = []
            return new_block
        else:
            self.update(miner,'punishment', 40)
            print (f"Something goes wrong with the {miner}, it generated invalid block")               
            self.poa_mine()
            return []
    
    def poc_mine(self):
        """
        Mines a new block by creating a new block from the pending transactions and adding it to the chain.
        Consensus : PoC
        """

        # Get the previous block in the chain
        previous_block = self.latest_block()        
        # Get the miner of the current block regarding to max token each one has
        selected_miner = self.select_miner_poc()        
        # Get the id of the new block
        id = previous_block.id + 1        
        # Mine the new block
        # Create a new block with the pending transactions 
        new_block = Block(id, self.pending_transactions, self.navigability, previous_block.hash,selected_miner)                              
        # Check the validation before add the block
        last_valid_block = self.chain[-1]
        if new_block.previous_hash == last_valid_block.hash:
            # Add the new block to the chain
            self.chain.append(new_block)
            # Clear the list of pending transactions
            self.pending_transactions = []
            return new_block
        else:
            self.update(selected_miner,'punishment', 40) 
            print (f"Something goes wrong with the {selected_miner[0]}, it generated invalid block")               
            self.poc_mine()
            return []        
            
    def latest_block(self):
        """
        Gets the latest block in the blockchain.

        Returns:
        Block: The latest block.
        """
        return self.chain[-1]

    def latest_transaction(self):
        """
        Gets the latest transaction in the blockchain.

        Returns:
        Transaction: The latest id.
        """
        #Looking through the pending transactions and last block to find the last id
        if len(self.pending_transactions) == 0 :
            return self.chain[-1].transactions[-1]
        elif len(self.pending_transactions) != 0:
            return self.pending_transactions[-1]    
                     
    def is_chain_valid(self):
        """
        Check the validation of the Blockchain

        Returns:
        True/False
        """                
        for i in range(self.chain[1], len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    
    def Retrieve(self,robot: str, com_robot: str):
        for block in self.chain[::-1]:
            for transaction in block.transactions[::-1]:
                if transaction.sender == robot and transaction.partner == com_robot:
                    return transaction    
  
    def landmarks_weight(self, robot_1: str, robot_2: str):
        find_transaction = 0
        landmarks = []
        weight = 0
        for transaction in self.pending_transactions[::-1]:
            if transaction.sender == robot_1 and transaction.partner == robot_2:
                find_transaction = 1
                landmarks = transaction.com_landmarks
                break
        if find_transaction == 0 :
            for block in self.chain[::-1]:
                for transaction in block.transactions[::-1]:
                    if transaction.sender==robot_1 and transaction.partner==robot_2 :
                        landmarks = transaction.com_landmarks
                        break
        if landmarks:
            for landmark in landmarks:
               weight += 1 / landmark[0]
        return weight

    def impact_factor(self, robot_1: str, robot_2: str):
        im_factor = 0
        for transaction in self.pending_transactions[::-1]:
            if transaction.sender == robot_1 and transaction.partner == robot_2:
                im_factor += 1
                if im_factor > 9 :
                   break
        for block in self.chain[::-1]:
            for transaction in block.transactions[::-1]:
                if transaction.sender==robot_1 and transaction.partner==robot_2 :
                    im_factor += 1
                    if im_factor > 9 :
                       break
        if im_factor > 0 :
           return im_factor / 10
        else:
           return 0
   
    def details(self):
        """
        Displays number of blocks in blockchain and legder .
        """
        print(f"Blockchain beasd on {self.consensus} includes        : {len(self.chain)} blocks")
        print(f"Number of generated blocks based on {self.consensus} : {len(self.chain)-1} blocks")


    def __repr__(self):
        return str(self.chain)

    
    def metric(self):
        """
        return the blockchain details.
        """
        return  [self.consensus, len(self.chain) , len(self.nodes), self.blockstimes]
        

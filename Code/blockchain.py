from transaction import Transaction
from block import Block
from node import Node
import hashlib
import random
import time
import datetime
import csv
import os
import heapq
from collections import deque

class Blockchain:
    """
    Represents a blockchain.
    """
    def __init__(self, consensus, modelName):
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
        self.start_time = datetime.datetime.now()
        # Create the genesis block
        self.create_genesis_block()
        self.blockstimes={}
        self.navigability=[]
        self.modelName = modelName
        

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
        # delta = time.mktime(time.strptime(time.ctime()))-time.mktime(time.strptime(self.latest_block().timestamp))
        delta = time.time() - self.latest_block().timestamp
           
        if len(self.pending_transactions) != 0 and (len(self.pending_transactions) >= len(self.nodes) or delta > 40):
            #start_time = time.ctime()
            # start_time = datetime.datetime.now()
            start_time = time.time()
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
                # end_time = datetime.datetime.now()
                end_time = time.time()
                duration = end_time - start_time
                self.blockstimes[self.chain[-1].id] = [start_time, end_time, duration]
        Success=self.chain[-1].id-fid 
        if Success != 1 :
            # print(F"The Block is not generated yet")
            # print(F"Number of pending transactions ({self.consensus}): {len(self.pending_transactions)}")
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
    
    def validation(self, navigation_matrix):
        n = len(navigation_matrix)
        result = []
        update_gen = {}
        for i in range(n):
            row_sum = 0
            for j in range(n):
                row_sum += navigation_matrix[i][j]
                name = f"{self.modelName}{i + 1}"
            update_gen[name] = row_sum
            result.append((name, row_sum))
        result.sort(key=lambda x: x[1], reverse=True)
        top_3_indices = [x[0] for x in result[:3]]
        selected_index = random.choice(top_3_indices)
        self.update_gen_csv(update_gen)
        return selected_index
    
    def select_miner_poc(self):
        """
        Using the navigability matrix of the last block and Select the best miner based on it.

        Returns:
        str: The selected validator.
        """
        if self.chain[-1].id > 1:
            navigation_matrix = self.chain[-1].navigability
        else:
            navigation_matrix = []
        num_nodes = len(self.nodes)
        # List of validators with their stakes.
        self.validators = {node['name']: node['privilege'] for node in self.nodes}
        self.update_validators_csv()
        if navigation_matrix:
            selected_validator = self.validation(navigation_matrix)    
        else:
            validator_names = list(self.validators.keys())
            selected_validator = random.choice(validator_names)     
        return selected_validator

    def update_navigability_csv(self):
        filename = f'navigability_matrix_{self.start_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        file_exists = os.path.isfile(filename)
        
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            names = [item['name'] for item in self.nodes]
            # Write headers if the file is newly created
            if not file_exists:
                headers = [''] + names # Column headers from dictionary keys
                writer.writerow(headers)
            
            # Write rows with row header and values
            for i, row in enumerate(self.navigability):
                row_header = [names[i]]  # Row header from dictionary keys
                writer.writerow(row_header + row)
            
            # Add an empty row for better readability
            # writer.writerow([])
            
    def update_validators_csv(self):
        filename = f'validators_values_{self.start_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        file_exists = os.path.isfile(filename)
        
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                # writer.writerow(['Validator', 'Values'])  # Header for the CSV file
                writer.writerow([validator for validator in self.validators])
            
            # Writing values for each validator in the same row
            row_values = [self.validators[validator] for validator in self.validators]
            writer.writerow(row_values)
            
    def update_gen_csv(self, update_gen):
        filename = f'update_gen_values_{self.start_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        file_exists = os.path.isfile(filename)
        
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                # writer.writerow(['Validator', 'Values'])  # Header for the CSV file
                writer.writerow([validator for validator in update_gen])
            
            # Writing values for each validator in the same row
            row_values = [update_gen[validator] for validator in update_gen]
            writer.writerow(row_values)
            
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
            self.update(selected_miner,'reward', 20) 
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
            self.update(selected_miner,'reward', 1) 
            # Clear the list of pending transactions
            self.pending_transactions = []
            return new_block
        else:
            self.update(selected_miner,'punishment', 4) 
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
    
    def transactions_weight(self, robot_1: str):
        w = 0
        if self.pending_transactions:
            total = self.pending_transactions[-1].id
        else:
            total = self.chain[-1].transactions[-1].id
        for transaction in self.pending_transactions[::-1]:
            if transaction.sender == robot_1:
                r_total = transaction.nonce
                w = r_total / total
                break
        if w == 0:
            for block in self.chain[::-1]:
                for transaction in block.transactions[::-1]:
                    if transaction.sender==robot_1:
                        r_total = transaction.nonce
                        w = r_total / total
                        break
                break
        return w
       
    def impact_factor(self, robot_1: str, robot_2: str):
        im_factor = 1
        for transaction in self.pending_transactions[::-1]:
            if transaction.sender == robot_1 and transaction.partner == robot_2:
                im_factor += 1
                if im_factor >= 10 :
                   break
        for block in self.chain[::-1]:
            for transaction in block.transactions[::-1]:
                if transaction.sender==robot_1 and transaction.partner==robot_2 and im_factor < 10:
                    im_factor += 1
                    if im_factor >= 10 :
                       break
        return im_factor/10

       
    def stack_weight(self, robot):
        validators = {node['name']: node['privilege'] for node in self.nodes}
        total_token = sum(validators.values())
        token = validators[robot]
        if total_token != 0:
            return token / total_token
        else:
            return 0
    
    def landmarks_weight(self, Matches):
        weight = 0
        if Matches:
            for landmark in Matches:
                weight += 1 / landmark[0]
        return weight
            
    def update_navigabilty(self, robot, partner, Matches, RMatches):
        robot_index = int(robot[len(self.modelName):]) - 1
        partner_index = int(partner[len(self.modelName):]) - 1
        impact_factor = self.impact_factor(robot, partner)
        robot_stack_weight = self.stack_weight(robot)
        partner_stack_weight = self.stack_weight(partner)
        robot_landmarks_weight = self.landmarks_weight(Matches)
        partner_landmarks_weight = self.landmarks_weight(RMatches)
        self.navigability[robot_index][partner_index] = robot_stack_weight * robot_landmarks_weight * impact_factor
        self.navigability[partner_index][robot_index] = partner_stack_weight * partner_landmarks_weight * impact_factor
        # Update navigability CSV
        self.update_navigability_csv()
        return

    def shortest_paths(self, start, target):
        start = int(start[len(self.modelName):]) - 1
        target = int(target[len(self.modelName):]) - 1
        distances = {node: float('inf') for node in range(len(self.navigability))}
        distances[start] = 0
        previous_nodes = {node: None for node in range(len(self.navigability))}
        priority_queue = [(0, start)]
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            if current_node == target:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = previous_nodes[current_node]
                return path[::-1], distances[target]
    
            for neighbor, weight in enumerate(self.navigability[current_node]):
                if weight > 0:  # Ignore zero weights (no connection)
                    distance = current_distance + weight
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous_nodes[neighbor] = current_node
                        heapq.heappush(priority_queue, (distance, neighbor))
        return [], float('inf')

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
        

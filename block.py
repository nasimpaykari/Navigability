import random
import hashlib
import time


class Block:
    """
    Represents a block in the blockchain.
    """

    def __init__(self, id: int, transactions: list, navigability: list, previous_hash: str, miner: str):
        """
        Initializes a new instance of the Block class.
        Args:
        id (int): The id of the block in the chain.
        transactions (list): The list of transactions in the block.
        timestamp (datetime): The timestamp of the block's creation.
        previous_hash (str): The hash of the previous block in the chain.
        miner (str): The robot which is responsible for generate the block.
        """
        self.id = id
        self.transactions = transactions
        self.navigability = navigability
        self.timestamp = time.ctime()
        self.previous_hash = previous_hash
        self.miner = miner
        self.hash = self.calculate_hash()
        #self.nonce = 0

    def calculate_hash(self):
        """
        Calculates the hash of the block.
        Returns:
        str: The hash of the block.
        """        
        block_string = f'{self.id}{self.transactions}{self.timestamp}{self.previous_hash}{self.miner}'
        return hashlib.sha256(block_string.encode()).hexdigest()  # or hashlib.md5(block_string.encode('utf-8'))

    def minted_block(self):
        """
        Current block minted.
        """
        print("Block mined by node {}".format(self.miner))        
        return self.timestamp
    
    def __repr__(self):
        return str(self.id)

    def details(self):
        """
        Print block details.
        """
        print("\tBlock id                : ", self.id)
        print("\tBlock Time              : ", self.timestamp)
        print("\tMiner                   : ", self.miner)
        print("\tBlock Hash              : ", self.hash)
        print("\tBlock Previous Hash     : ", self.previous_hash)
        print("\tNumber of Transactions  : ", len(self.transactions))
        
    def metric(self):
        """
        return the block details.
        """
        return  [self.id, self.miner, len(self.transactions), self.timestamp, self.navigability]

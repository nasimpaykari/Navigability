from transaction import Transaction
from block import Block
from node import Node
from blockchain import Blockchain

# from network_module import load_network_csv, create_network
#from M_ALV2 import CommonLandmarkPanos #does not work -->ImportError: cannot import name 'CommonLandmarkPanos' from partially initialized module 'M_ALV2' (most likely due to a circular import) (/home/labaccount/ROS/wavn/consensusmodels/M_ALV2.py)
import time
import sys
import random
import threading    
import csv

# ROS
# import M_ALV2 as ma
# Simulation!
import wavnsim as ws


consensuses={"poc":True, "pos":False, "pow":False , "dpos":False, "poa":False}

    
def initialize_blockchain():
    global tx_dicts_panoramics
    global blockchains
    global authorities_list
    
    blockchains={}
    tx_dicts_panoramics={}
    for consensus,enabled in consensuses.items():
        if enabled :
            blockchains[consensus] = Blockchain(consensus)
            if consensus == "poa" :
                authorities_list = ["P1"]
            print (f"Blockchain based on {consensus} consensus is started.")
            
    tx_dicts_panoramics = {}
    #for blockchain in blockchains.values():
        #print(blockchain.nodes)
           
def reference_blockchain(consensuses,blockchains):
    for consensus,enabled in consensuses.items():
        if enabled :
            return blockchains[consensus]
            
            
def node_generator(modelname,robotsnum):
    for consensus,blockchain in blockchains.items():
        node_generatorIn(blockchain,modelname,robotsnum)        
    

def node_generatorIn(blockchain,modelname,robotsnum):
    '''
    Generated a list of 'len(team)' nodes based on model name
    '''
    for i in range(robotsnum):
        Node.add_node(i, f"{modelname}{i+1}")
        #print(f"Blockchain: the node of {modelname}{i+1} is generated")
    blockchain.nodes = Node.get_all_nodes()
              
    for node in blockchain.nodes:
        blockchain.nonce[node["name"]] = 0
        if blockchain.consensus == "pow" :
            blockchain.update(node["name"],"start", 0)
        elif blockchain.consensus == "pos" :
            blockchain.update(node["name"],"start", 50)
        elif blockchain.consensus == "poc" :
            blockchain.update(node["name"],"start", 0)
        elif blockchain.consensus == "dpos": 
            blockchain.update(node["name"],"start", 1)   
        elif blockchain.consensus == "poa" :
            if node["name"] in authorities_list :
                blockchain.update(node["name"],"start", 1)
    print(blockchain.nodes) 

       
def UpdatePanoramicView(bot,robot: str, panoramic: list):
    """
    Add panoramics and common landmarks to the ledger.
    Gets the latest panoramic from the ledger of the rest of the robots, and creates
    a new transactions with the provided panoramic.

    """
    global tx_dicts_panoramics
    
    
    # Find the last panorama for other robots and add them to the a temporary dictionary 
    for transaction in reference_blockchain(consensuses,blockchains).pending_transactions:
        if transaction.sender != robot:
            tx_dicts_panoramics[transaction.sender] = transaction.panorama
                            
    for node1 in reference_blockchain(consensuses,blockchains).nodes:
        for node2 in reference_blockchain(consensuses,blockchains).nodes:
            if node1["name"] != robot and node1["name"] != node2["name"] and node1["name"] not in tx_dicts_panoramics:
                if Blockchain.Retrieve(reference_blockchain(consensuses,blockchains),node1["name"],node2["name"]) is not None:
                    tx_dicts_panoramics[node1["name"]] = Blockchain.Retrieve(reference_blockchain(consensuses,blockchains),node1["name"],node2["name"]).panorama
   
    # Add the robot's panorama to the tx_dicts_panoramics                           
    if tx_dicts_panoramics.get(robot) is None :
        for _,blockchain in blockchains.items():
            if blockchain.consensus == "pos":     
                blockchain.update(robot,'add_panoramic', 5) 
    tx_dicts_panoramics[robot] = panoramic
  
    Success={"pow":0, "pos":0, "dpos":0, "poa":0, "poc":0}       
    # Find the common landmarks
    for comp_robot, comp_panoramic in tx_dicts_panoramics.items():
        if robot != comp_robot :
            Matches,RMatches = ma.CommonLandmarkPanos(bot, panoramic, comp_panoramic, robot, comp_robot)
            if len(Matches) != 0:
                for consensus,blockchain in blockchains.items():
                    Tx_1=Transaction(blockchain.latest_transaction().id+1, robot, panoramic, comp_robot, Matches, blockchain.nonce[robot])
                    if Tx_1 != Blockchain.Retrieve(blockchain,robot,comp_robot) and Tx_1 not in blockchain.pending_transactions:
                        blockchain.add_transaction(Tx_1)
                        #Tx_1=[]
                        blockchain.nonce[robot]+=1
                        if blockchain.consensus == "pos":
                            blockchain.update(robot,'common_landmark', 10)
                        elif blockchain.consensus == "poc":
                            blockchain.update(robot,'common_landmark', len(Matches))
                            blockchain.update(comp_robot,'common_landmark', len(RMatches))
                        elif blockchain.consensus == "dpos" and Node.get_node_by_name(comp_robot).privilege > 0:
                            blockchain.update(comp_robot,'common_landmark', 10)                   
                    Tx_2=Transaction(blockchain.latest_transaction().id+1, comp_robot, comp_panoramic, robot, RMatches, blockchain.nonce[comp_robot])
                    if Tx_2 != Blockchain.Retrieve(blockchain,comp_robot,robot)  and Tx_2 not in blockchain.pending_transactions: 
                        blockchain.add_transaction(Tx_2)
                        blockchain.nonce[comp_robot]+=1
                        Tx_2=[]
                    Success[consensus],Newblock = blockchain.generate_block()              
                    if len(blockchain.pending_transactions) != 0 and len(blockchain.pending_transactions) >= len(blockchain.nodes):
                        while Success[consensus] != 1:
                            print(f'{consensus} consensus did not generate the block, it will try again after 5 seconds')
                            time.sleep(5)
                            Success[consensus],Newblock = blockchain.generate_block()
                    #print("Success dic",Success)
                    #if Success[consensus] == 1 :
                        #blockchain.details()
                        #display(blockchain,"last")
                    #else:
                        #display(blockchain,"pending") 
                                                          
    enabled_consensus=[consensus for consensus,enabled in consensuses.items() if enabled]
    if all(Success.get(consensus,False) == 1 for consensus in enabled_consensus):
        tx_dicts_panoramics.clear()
  
       
def display(blockchain,arg: str):
    if arg == "all":       
        blockchain.details()
        for block in blockchain.chain :
            block.details()
            for transaction in block.transactions :
                transaction.details()
    elif arg == "pending":
        for transaction in blockchain.pending_transactions:
            transaction.details()
    elif arg == "last":
        Last_Block=blockchain.latest_block()
        Last_Block.details()
        for transaction in Last_Block.transactions :
            transaction.details()                   
    else:
        print('Wrong argument for display of blockchain details; Please use "All" or "Last"') 
        
def navigation_update(navigability, filename):
    try:
        existing_data = np.loadtxt(filename, delimiter=',')
        updated_data = np.vstack([existing_data, navigability])
    except FileNotFoundError:
        updated_data = navigability

    np.savetxt(filename, updated_data, delimiter=',')

def metric(arg: str, timestamp, num):
    if arg == "blockchains":
        file_name = f"Log_{num}_{arg}_{timestamp}.csv"
        blockchain_headers = ["Consensus", "Number of Blocks", "Number of Nodes", "Block Number", "Start", "End", "Duration"]
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=blockchain_headers)
            writer.writeheader()
            for consensus, blockchain in blockchains.items():
                consensus, number_of_blocks, number_of_nodes, blocks_times = blockchain.metric()
                for id, block_times in blocks_times.items():
                    block_info = {
                        "Consensus": consensus,
                        "Number of Blocks": number_of_blocks,
                        "Number of Nodes": number_of_nodes,
                        "Block Number": id,
                        "Start": block_times[0],
                        "End": block_times[1],
                        "Duration" : block_times[2]
                    }
                    writer.writerow(block_info)
                print(f"Metric parameters of blockchain based on {consensus} have been updated.")
        csvfile.close()        
    elif arg == "blocks":
        file_name = f"Log_{num}_{arg}_{timestamp}.csv"
        block_headers = ["Consensus", "Block id", "Miner", "Number of Transactions", "Time"]
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = block_headers)
            writer.writeheader()
            for consensus,blockchain in blockchains.items() :
                for block in blockchain.chain :
                    id, miner, number_of_transactions,time = block.metric()
                    block_info  = { 
                        "Consensus" : consensus,
                        "Block id" : id, 
                        "Miner" : miner,
                        "Number of Transactions" : number_of_transactions, 
                        "Time" : time 
                    }    
                    writer.writerow(block_info)
                print(f"Metric parameters of blocks based on {consensus} have been updated. ")
        csvfile.close()
    elif arg == "transactions":
        file_name = f"Log_{num}_{arg}_{timestamp}.csv"
        transaction_headers = ["Consensus", "Block Number", "Tansaction id", "Sender", "Nonce", "Partner", "Com_landmarks", "Time"]
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = transaction_headers)
            writer.writeheader()
            for consensus,blockchain in blockchains.items() :
                for block in blockchain.chain :
                    for transaction in block.transactions :  
                        tansaction_id, sender, nonce, partner, com_landmarks, time = transaction.metric()
                        transaction_info = {
                            "Consensus" : consensus,
                            "Block Number" : block.id,
                            "Tansaction id" : tansaction_id,
                            "Sender" : sender,
                            "Nonce" : nonce, 
                            "Partner" : partner,  
                            "Com_landmarks" : com_landmarks,
                            "Time" : time
                        }
                        writer.writerow(transaction_info)
            print(f"Metric parameters of transactions based on {consensus} have been updated. ") 
        csvfile.close()              
    else:
        print('Wrong argument for display of blockchain details; Please use "blockchain" , "blocks" or "transactions')     
    
def RetrievePanoramicView(robot_1: str, robot_2: str):
    find_transaction = 0
    #print(f"Call RetrievePanoramicView:_____________for {robot_1} and {robot_2}")
    for transaction in reference_blockchain(consensuses,blockchains).pending_transactions[::-1]:
        if transaction.sender == robot_1 and transaction.partner == robot_2:
            find_transaction = 1
            #print("RetrievePanoramicView:_____________pending",transaction.details())
            return transaction.panorama,transaction.com_landmarks
    if find_transaction == 0 :
        for block in reference_blockchain(consensuses,blockchains).chain[::-1]:
            for transaction in block.transactions[::-1]:
                if transaction.sender==robot_1 and transaction.partner==robot_2 :
                    #print("RetrievePanoramicView:_____________blockchain",transaction.details())
                    return transaction.panorama,transaction.com_landmarks
    #print("RetrievePanoramicView:_____________Not Found")
    #display(reference_blockchain(consensuses,blockchains),"all")
    return[],[]
                   
def broadcast(data,sent_by,type_):
    #for j in [i for i in Node.get_all_nodes() if i["name"] != sender]:
    for i in Node.get_all_nodes():
        latency=node_map_del[i["name"]][sent_by]
        if i["name"] != sent_by:
            receiver(data,sent_by,i["name"],type_,latency)


def receiver(data,sent_by,receive_by,type_,latency):
    if type_== "Transaction":
        if data not in blockchain.pending_transactions:
            blockchain.pending_transactions.append(data)
    if type_== "Block":
        if blockchain.latest_block().id != data.id:
            blockchain.append(data)
            transactions_pool=[]              

# Exp file for Nasim's consensus model testing
# Jan 2024

from transaction import Transaction
from block import Block
from node import Node
from blockchain import Blockchain
import random
import time
import csv
import math
import poc
import numpy as np
import matplotlib.pyplot as plt

print("New Test")

# ROS
# import wavn as wv
# Simulation!
import wavnsim as ws
    
team = [i for i in range(0,10)]
modelName='P'
numberoflandmarks = 20
sim_world = ws.world(modelName, len(team), numberoflandmarks)
#print("Robots : ========================")
#print(sim_world.robots)
#print("Common Landmarks===========================")
#print(sim_world.common)
#Matches,RMatches = sim_world.CommonLandmarkPanos("P1", "P2")
#print("Common Landmarks Matches P1 and P2: ===========================")
#print(Matches)
#print("RMatches: ")
#print(RMatches)

poc.initialize_blockchain()
poc.node_generator(modelName, len(team))

for i in range(0, 10):
    print(f"\nLoop number {i} has been started: \n")
    filename = f"{len(team)}_{i}_{time.ctime}"
    sim_world.drawWorld(filename)
    for robot in team :
        robot_name = f"{modelName}{robot+1}"
        for comp_robot in team:
            comp_robot_name = f"{modelName}{comp_robot+1}"
            if robot != comp_robot:
               Matches,RMatches = sim_world.CommonLandmarkPanos(robot_name, comp_robot_name)
               if Matches:
                  #print(f"Common Landmarks Matches {robot_name} and {comp_robot_name}: {Matches}")
                  poc.UpdateView(robot_name, comp_robot_name, Matches, RMatches)
        time.sleep(random.randint(1,2))
    sim_world.move()
filename = f"{len(team)}_moves_{time.ctime}"
sim_world.movements(filename)            
poc.metric("blockchains",time.ctime,len(team))
poc.metric("transactions",time.ctime,len(team))
poc.metric("blocks",time.ctime,len(team))


input("Press Enter to exit...")

    

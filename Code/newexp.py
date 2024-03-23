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

for i in range(0, 5):
    print(f"\nLoop number {i} has been started: \n")
    filename = f"{len(team)}_{i}_{time.ctime()}"
    sim_world.drawWorld(filename)
    for robot in team :
        robot_name = f"{modelName}{robot+1}"
        num=random.randint(1,100)
        print(F"Random number is {num} for {robot_name}")
        if num > 50:
            print(F"{robot_name} looks around")
            for comp_robot in team:
                comp_robot_name = f"{modelName}{comp_robot+1}"
                if robot != comp_robot:
                    Matches,RMatches = sim_world.CommonLandmarkPanos(robot_name, comp_robot_name)
                    if Matches:
                        #print(f"Common Landmarks Matches {robot_name} and {comp_robot_name}: {Matches}")
                        poc.UpdateView(robot_name, comp_robot_name, Matches, RMatches)
        time.sleep(random.randint(1,2))
    random_bot = random.choice(team)
    robot_searcher = f"{modelName}{random_bot+1}"
    print(F"{robot_searcher} looks for home")
    targets = sim_world.see_home_of_robot(robot_searcher)
    print(f"The list of robot who can see {robot_searcher}'s home: {targets}")
    if targets:
        for traget in targets:
            # poc.shortest_paths(random_bot, traget)
            print("Shortest paths: ",poc.shortest_paths(modelName, robot_searcher, traget))
    sim_world.move()
filename = f"{len(team)}_moves_{time.ctime()}"
sim_world.movements(filename)            
poc.metric("blockchains",time.ctime(),len(team))
poc.metric("transactions",time.ctime(),len(team))
poc.metric("blocks",time.ctime(),len(team))


input("Press Enter to exit...")

    

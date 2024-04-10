# Exp file for Nasim's consensus model testing
# Jan 2024

from transaction import Transaction
from block import Block
from node import Node
from blockchain import Blockchain
import random
import time
import datetime
import csv
import math
import os
import poc
import numpy as np
import matplotlib.pyplot as plt

# Function to write data to CSV
def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Start Time', 'Robot Action', 'Matches', 'Robot Searching for Home', 'Targets', 'Shortest Paths', 'End Time'])
        writer.writerows(data)

print("New Test")

# ROS
# import wavn as wv
# Simulation!
import wavnsim as ws

modelName='P'    
team = [f"{modelName}{i+1}" for i in range(0,10)]
numberoflandmarks = 30
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

poc.initialize_blockchain(modelName)
poc.node_generator(modelName, len(team))

start_time = time.time()
start_datetime = datetime.datetime.fromtimestamp(start_time)

data = []
for i in range(0, 100):
    print(f"\nLoop number {i} has been started: \n")
    loop_start_time = time.time()
    filename_world = filename = f"{len(team)}_{i}_{start_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    sim_world.drawWorld(filename_world)
    for robot in team :
        num=random.randint(1,100)
        # print(F"Random number is {num} for {robot}")
        matches = []
        if num > 50:
            print(F"{robot} moves and looks around")
            sim_world.move(robot)
            for comp_robot in team:
                if robot != comp_robot:
                    Matches, RMatches = sim_world.CommonLandmarkPanos(robot, comp_robot)
                    if Matches:
                        #print(f"Common Landmarks Matches {robot_name} and {comp_robot_name}: {Matches}")
                        matches.append((robot, comp_robot, Matches))
                    poc.UpdateView(modelName, robot, comp_robot, Matches, RMatches)
            action = f"{robot} moved and looked around"
        else:
            action = f"{robot} did not move!"
        time.sleep(random.randint(1,2))
        # Append data for CSV
        data.append([time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(loop_start_time)), action, matches, '', '', '', ''])
    robot_searcher = random.choice(team)
    action = f"{robot_searcher} looks for home"
    print(F"{robot_searcher} looks for home")
    targets = sim_world.see_home_of_robot(robot_searcher)
    print(f"The list of robot who can see {robot_searcher}'s home: {targets}")
    # Append data for CSV
    data[-1][3] = robot_searcher
    data[-1][4] = targets
    shortest_paths = []
    if targets:
        shortest_paths = []
        for target in targets:
            shortest_path_to_target,_ = poc.shortest_path(robot_searcher, target)
            convert_shortest_paths = []
            if shortest_path_to_target:
                robots_path = [f"{modelName}{num+1}" for num in shortest_path_to_target]
                shortest_paths.append(robots_path)    
                print(f"Shortest paths through the {target}: {robots_path}")
    # Sort shortest_paths based on the length of its elements (sublists)
    shortest_paths = sorted(shortest_paths, key=lambda x: len(x))
    print(f"Shortest paths : {shortest_paths}")
    # Append data for CSV  
    data[-1][5] = shortest_paths
    loop_end_time = time.time()
    # Append data for CSV
    data[-1][-1] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(loop_end_time))

# Write data to CSV
filename_info = f"{len(team)}_{i}_{start_datetime.strftime('%Y-%m-%d_%H-%M-%S')}_simulation_data.csv"
write_to_csv(data, filename_info)

sim_world.movements(filename_world)
poc.metric("blockchains",filename_info,len(team))
poc.metric("transactions",filename_info,len(team))
poc.metric("blocks",filename_info,len(team))


# input("Press Enter to exit...")

    

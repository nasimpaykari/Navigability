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

start_time = time.time()
start_datetime = datetime.datetime.fromtimestamp(start_time)

data = []
for i in range(0, 100):
    print(f"\nLoop number {i} has been started: \n")
    loop_start_time = time.time()
    filename_world = filename = f"{len(team)}_{i}_{start_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    sim_world.drawWorld(filename_world)
    for robot in team :
        robot_name = f"{modelName}{robot+1}"
        num=random.randint(1,100)
        print(F"Random number is {num} for {robot_name}")
        matches = []
        if num > 50:
            action = f"{robot_name} looks around"
            print(F"{robot_name} looks around")
            for comp_robot in team:
                comp_robot_name = f"{modelName}{comp_robot+1}"
                if robot != comp_robot:
                    Matches, RMatches = sim_world.CommonLandmarkPanos(robot_name, comp_robot_name)
                    if Matches:
                        #print(f"Common Landmarks Matches {robot_name} and {comp_robot_name}: {Matches}")
                        poc.UpdateView(robot_name, comp_robot_name, Matches, RMatches)
                        matches.append((robot_name, comp_robot_name, Matches))
        else:
            action = None
        time.sleep(random.randint(1,2))
        # Append data for CSV
        data.append([time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(loop_start_time)), action, matches, '', '', '', ''])
    random_bot = random.choice(team)
    robot_searcher = f"{modelName}{random_bot+1}"
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
            shortest_paths_to_target = poc.shortest_paths(modelName, robot_searcher, target)
            convert_shortest_paths = []
            for path in shortest_paths_to_target:
                robots_path = [f"{modelName}{num+1}" for num in path]
                convert_shortest_paths.append(robots_path)
            shortest_paths.append(convert_shortest_paths)    
            print(f"Shortest paths through the {target}: {convert_shortest_paths}")
    # Sort shortest_paths based on the length of its elements (sublists)
    shortest_paths = sorted(shortest_paths, key=lambda x: len(x))
    print(f"Shortest paths : {shortest_paths}")
    # Append data for CSV  
    data[-1][5] = shortest_paths
    loop_end_time = time.time()
    # Append data for CSV
    data[-1][-1] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(loop_end_time))

    sim_world.move()
# Write data to CSV
filename_info = f"{len(team)}_{i}_{start_datetime.strftime('%Y-%m-%d_%H-%M-%S')}_simulation_data.csv"
write_to_csv(data, filename_info)

sim_world.movements(filename_world)
poc.metric("blockchains",filename_info,len(team))
poc.metric("transactions",filename_info,len(team))
poc.metric("blocks",filename_info,len(team))


input("Press Enter to exit...")

    

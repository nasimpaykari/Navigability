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
    
print("New Test")

# ROS
# import wavn as wv
# Simulation!
import wavnsim as ws

modelName='P'    
team = [f"{modelName}{i+1}" for i in range(0,10)]
numberoflandmarks = 30
sim_world = ws.world(modelName, len(team), numberoflandmarks)

poc.initialize_blockchain(modelName)
poc.node_generator(modelName, len(team))

start_time = time.ctime()
filename = f"{len(team)}_exp_{start_time}"
filename_world = f"Log_{len(team)}_exp_{start_time}.csv"
sim_world.drawWorld(f"Log_{len(team)}_Start_world_{start_time}.pdf")
headers = ['Loop No.', 'Start'] + team +['Searcher', 'Targets', 'Paths', 'End']
lookaround = [0]*len(team)
header_write = 0

for i in range(0, 100):
    print(f"\nLoop number {i} has been started: \n")
    loop_start_time = time.time()
    for robot in team :
        num=random.randint(1,100)
        # print(F"Random number is {num} for {robot}")
        matches = []
        if num > 50:
            print(F"{robot} moves and looks around")
            sim_world.move(robot)
            lookaround[int(robot[len(modelName):]) - 1] = 1
            for comp_robot in team:
                if robot != comp_robot:
                    Matches, RMatches = sim_world.CommonLandmarkPanos(robot, comp_robot)
                    # if Matches:
                        # print(f"Common Landmarks Matches {robot_name} and {comp_robot_name}: {Matches}")
                        # matches.append((robot, comp_robot, Matches))
                    poc.UpdateView(modelName, robot, comp_robot, Matches, RMatches)
        else:
            lookaround[int(robot[len(modelName):]) - 1] = 0
        # time.sleep(random.randint(1,2))
        time.sleep(2)
    robot_searcher = random.choice(team)
    print(f"{robot_searcher} looks for home")
    targets = sim_world.see_home_of_robot(robot_searcher)
    print(f"The list of robot who can see {robot_searcher}'s home: {targets}")
    # Append data for CSV
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
    loop_end_time = time.time()
    with open(filename_world, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = headers)
        if not header_write :
            writer.writeheader()
            header_write = 1
        info  = { "Loop No." : i, "Start" : loop_start_time, "End" : loop_end_time }   
        for index, bot in enumerate(team) :
            info.update({bot :lookaround[index]})
        info.update( {"Searcher" : robot_searcher, "Targets" : targets, "Paths" : shortest_paths}) ##"Path" : path
        writer.writerow(info)
        print(f"Metric parameters of consensus expriment have been updated. ")
        csvfile.close()

sim_world.movements(f"Log_{len(team)}_world_Moves_{start_time}.pdf")
poc.metric("blockchains",filename,len(team))
poc.metric("transactions",filename,len(team))
poc.metric("blocks",filename,len(team))


# input("Press Enter to exit...")

    

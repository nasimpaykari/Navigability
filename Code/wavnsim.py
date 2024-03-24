import numpy as np
import random
import matplotlib.pyplot as plt

class world():
    def __init__(self, modelname: str, nRobots: 2, nLandmarks: 5):     
        """
        Initialize the World class.

        Parameters:
            modelname (str): A string representing the model name.
            nRobots (int): Number of robots to be created (default is 2).
            nLandmarks (int): Number of landmarks to be created (default is 5).
        """     
        # Constants for map elements
        self.robotMark = 99
        self.landMark = 40
        self.lineMark = 12
        self.pathMark1 = 60
        self.pathMark2 = 80
        
        # Parameters for world size and range
        self.rlRange=50
        self.worldX=200
        self.worldY=200
        # Initialize the map
        self.map = np.zeros((self.worldX,self.worldY))
        
        # Create the world
        self.robots = []
        self.positions = {}
        self.landmarks = []
        self.homelandmark = {}     
        self.makeWorld(modelname, nRobots, nLandmarks)
        self.Home()
        
        # List to store common landmarks between robots
        self.findCommon()


    def makeWorld(self, modelname, nRobots, nLandmarks):
        """
        Generate random positions for robots and landmarks within the world boundaries.

        Parameters:
            modelname (str): A string representing the model name.
            nRobots (int): Number of robots to be created.
            nLandmarks (int): Number of landmarks to be created.
        """
        xrange=[0,self.worldX]
        yrange=[0,self.worldY]
        
        # Generate random positions for robots
        for r in range(nRobots):
            name = f"{modelname}{r+1}"
            x = random.randrange(xrange[0]+5,xrange[1]-5)
            y = random.randrange(yrange[0]+5,yrange[1]-5)
            self.robots.append([name,[x,y]])
            self.positions[name] = [(x,y)]
        
        # Generate random positions for landmarks
        for r in range(nLandmarks):
            x = random.randrange(xrange[0]+5,xrange[1]-5)
            y = random.randrange(yrange[0]+5,yrange[1]-5)
            self.landmarks.append((x,y))

    def Home(self):
        """
        Assign a random landmark as "home" to each robot.
        """
        for r in self.robots:
            home_landmark = random.choice(self.landmarks)
            self.homelandmark[r[0]] = home_landmark

    def move(self):
        """
        Move the robots to random positions within the maximum range.
        """
        xrange = [0, self.worldX]
        yrange = [0, self.worldY]
        moved_robots = []  # List to store names of robots that moved

        # Calculate maximum movement range (1/50th of the world size)
        max_range_x = self.worldX / 4
        max_range_y = self.worldY / 4

        # Move robots to random positions within the maximum range
        for r in self.robots:
            should_move = random.choice([True, True, False])  # Randomly decide whether to move the robot
            if should_move:
                move_x = random.uniform(-max_range_x, max_range_x)
                move_y = random.uniform(-max_range_y, max_range_y)

                # Update robot position
                new_x = max(min(r[1][0] + move_x, xrange[1] - 5), xrange[0] + 5)
                new_y = max(min(r[1][1] + move_y, yrange[1] - 5), yrange[0] + 5)
                r[1][0] = new_x
                r[1][1] = new_y

                self.positions[r[0]].append((new_x, new_y))
                moved_robots.append(r[0])  # Record the name of the robot that moved

        self.findCommon()

        # Print the names of robots that moved
        print("Robots that moved:", moved_robots)
        

    def findCommon(self):
        """
        Find common landmarks between robots.
        """
        self.common = []
        for r1 in self.robots:
            robots1 = list(self.robots)
            robots1.remove(r1)
            for r2 in robots1:
                cl = []
                for l in self.landmarks:
                    d1 = np.hypot(r1[1][0]-l[0], r1[1][1]-l[1])
                    d2 = np.hypot(r2[1][0]-l[0], r2[1][1]-l[1])
                    if d1<self.rlRange and d2<self.rlRange:
                        q = random.randrange(5,200)
                        cl.append([l,q])
                if len(cl)>0:
                    self.common.append((r1,r2,cl))             
        return

    def CommonLandmarkPanos(self, robot_1, robot_2):
        """
        Find common landmarks between two specified robots.

        Parameters:
            robot_1 (str): Name of the first robot.
            robot_2 (str): Name of the second robot.

        Returns:
            Matches (list): List of common landmarks between the specified robots.
            RMatches (list): List of reverse common landmarks between the specified robots.
        """
        Matches,RMatches = [], []
        if self.common != 0:
            for cls in self.common:
                if cls[0][0] == robot_1 and cls[1][0] == robot_2:
                    for cl in cls[2]:
                        c_1 = random.randrange(0,6)
                        c_2 = random.randrange(0,6)
                        Matches.append([cl[1],cl[0][0],cl[0][1], (c_1,c_2)])
                        RMatches.append([cl[1],cl[0][0],cl[0][1], (c_2,c_1)])      
        return Matches,RMatches
        
    def drawWorld(self, filename=None):
        """
        Draw the world with robots, landmarks, and common landmarks between robots.

        Parameters:
            filename (str): Name of the file to save the plot as a PDF (optional).
        """
        # Plot the world using matplotlib
        plt.figure(figsize=(8, 8))
        plt.imshow(self.map, cmap='PuRd', origin='upper')

        # Plot common landmarks between robots
        for m in self.common:
            r=m[0][1]
            r1=m[1][1]
            x,y=r[0],r[1]
            for l in m[2]:
                x1,y1=l[0][0],l[0][1]
                # self.doLine((x,y), (x1,y1))
                plt.plot([x, x1], [y, y1], color='black', linewidth=0.5)
                
        # Plot robots and landmarks             
        for robot in self.robots:
            self.drawRobot(robot)
        for landmark in self.landmarks:
            self.drawLandmark(landmark)

        # Save figure to PDF if filename is provided
        if filename:
            plt.savefig(filename, format='pdf', bbox_inches='tight')
                    
        # plt.show()
        # plt.pause(0.1)
        return

    def doLine(self, s,e):
        """
        Draw a line between two points on the map.

        Parameters:
            s (tuple): Starting point of the line.
            e (tuple): Ending point of the line.
        """
        xdiff = float(e[0]-s[0])
        ydiff = float(e[1]-s[1])
        res=100.0
        for i in range(0,int(res)):
            x=s[0]+i*float(xdiff/res)
            y=s[1]+i*float(ydiff/res)
            if 0<=x<self.worldX and 0<=y<self.worldY:
                self.map[int(x)][int(y)]=self.lineMark   

    def drawRobot(self, p):
        """
        Draw a robot on the map.

        Parameters:
            p (list): Robot details including its name and position.
        """
        plt.plot(p[1][0], p[1][1], marker='s', markersize=10, markerfacecolor='white', markeredgecolor='blue', markeredgewidth=1)
        plt.text(p[1][0], p[1][1], p[0], fontsize=8, color='black', ha='center', va='center')     
        #for x in [p[0]-1,p[0],p[0]+1]:
            #self.map[x][p[1]]=self.robotMark
        #for y in [p[1]-1,p[1],p[1]+1]:
            #self.map[p[0]][y]=self.robotMark
        return


    def drawLandmark(self,p):
        """
        Draw a landmark on the map.

        Parameters:
            p (tuple): Coordinates of the landmark.
        """
        # Plot landmark as a circle
        plt.plot(p[0], p[1], marker='o', markersize=8, color='red')
        #for x in [p[0]-1,p[0],p[0]+1]:
            #for y in [p[1]-1,p[1],p[1]+1]:
                #self.map[x][y]=self.landMark
        #self.map[p[0]][p[1]]=0
        return
        
    def movements(self, filename):
        """
        Plot movements of each robot on the map.

        Parameters:
            filename (str): Name of the file to save the plot as a PDF.
        """
        plt.figure(figsize=(8, 8))
        plt.imshow(self.map, cmap='PuRd', origin='upper')
        for robot, positions in self.positions.items():
            x, y = zip(*positions)
            plt.plot(x, y, label=robot, marker='o')

        # Add labels and legend
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Movements for Each Robot')
        plt.legend()
        plt.savefig(filename, format='pdf', bbox_inches='tight')
        plt.pause(0.1)
        return

    def see_home_of_robot(self, robot_name):
        """
        Find robots that can see the home of the specified robot.

        Parameters:
            robot_name (str): Name of the robot.

        Returns:
            robots_seeing_home (list): List of robots that can see the home of the specified robot.
        """
        robots_seeing_home = []
        robot_home = self.homelandmark[robot_name]
        for robot, position in self.positions.items():
            x, y = position[-1]  # Current position of the robot
            distance_to_home = np.hypot(robot_home[0] - x, robot_home[1] - y)
            if distance_to_home < self.rlRange:  # If the home is within sensing range
                robots_seeing_home.append(robot)
        return robots_seeing_home

# Create a world instance
w = world(modelname="P", nRobots=5, nLandmarks=20)

# Draw the initial world
w.drawWorld(filename="initial_world.pdf")

# show the Home position for each robot
print("home: ",w.homelandmark)

# Get common landmarks between two robots
matches, reverse_matches = w.CommonLandmarkPanos("P1", "P2")
print("Matches between 'P1' and 'P2':")
print("Matches:", matches)
print("Reverse Matches:", reverse_matches)

print("Robots are moved!")
# Move the robots
w.move()

# Draw the world after movement
w.drawWorld(filename="world_after_movement.pdf")

# Get common landmarks between two robots
matches, reverse_matches = w.CommonLandmarkPanos("P1", "P2")
print("Matches between 'P1' and 'P2':")
print("Matches:", matches)
print("Reverse Matches:", reverse_matches)

# Show movements of each robot
w.movements(filename="robot_movements.pdf")

# See which robots can see the home of robot "P1"
robots_seeing_home_of_P1 = w.see_home_of_robot("P1")
print("Robots seeing the home of 'P1':", robots_seeing_home_of_P1)


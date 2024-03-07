import numpy as np
import random
import matplotlib.pyplot as plt

class world():
   def __init__(self, modelname: str, nRobots: 2, nLandmarks: 5):     
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
      self.makeWorld(modelname, nRobots, nLandmarks)
      
      # List to store common landmarks between robots
      self.findCommon()


   def makeWorld(self, modelname, nRobots, nLandmarks):
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
    
   def move(self):
      xrange=[0,self.worldX]
      yrange=[0,self.worldY]
      # Move robots to random positions within the world
      for r in self.robots:
          r[1][0] = random.randrange(xrange[0]+5,xrange[1]-5)
          r[1][1] = random.randrange(yrange[0]+5,yrange[1]-5)
          self.positions[r[0]].append((r[1][0],r[1][1]))
      self.findCommon()
        
    
   def findCommon(self):
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
                  
       #plt.show()
       plt.pause(0.1)
       return

   def doLine(self, s,e):
       xdiff = float(e[0]-s[0])
       ydiff = float(e[1]-s[1])
       res=100.0
       for i in range(0,int(res)):
           x=s[0]+i*float(xdiff/res)
           y=s[1]+i*float(ydiff/res)
           if 0<=x<self.worldX and 0<=y<self.worldY:
               self.map[int(x)][int(y)]=self.lineMark   

   def drawRobot(self, p):
        plt.plot(p[1][0], p[1][1], marker='s', markersize=10, markerfacecolor='white', markeredgecolor='blue', markeredgewidth=1)
        plt.text(p[1][0], p[1][1], p[0], fontsize=8, color='black', ha='center', va='center')     
        #for x in [p[0]-1,p[0],p[0]+1]:
            #self.map[x][p[1]]=self.robotMark
        #for y in [p[1]-1,p[1],p[1]+1]:
            #self.map[p[0]][y]=self.robotMark
        return


   def drawLandmark(self,p):
        # Plot landmark as a circle
        plt.plot(p[0], p[1], marker='o', markersize=8, color='red')
        #for x in [p[0]-1,p[0],p[0]+1]:
            #for y in [p[1]-1,p[1],p[1]+1]:
                #self.map[x][y]=self.landMark
        #self.map[p[0]][p[1]]=0
        return
        
   def movements(self, filename):
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

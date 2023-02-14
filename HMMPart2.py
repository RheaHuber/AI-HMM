# HMM Car Tracker
# Finds the most likely location of a hidden car using approx. distances measured from a moving agent car
# Receives sensor data input file, transition prob input file, and end time from command line
# Sensor data is a .csv file containing an ordered list of X,Y positions the agent car travels through,
# the sensor reading received at each, and the dimensions N of the grid the cars occupy
# Transition data is a .csv file containing a list of X,Y positions on the grid and the probability of the
# hidden car traveling in each cardinal direction from that position
# Returns a .csv file containing an NxN grid of calculated probability values for the hidden car's position

# Import sys to access command line arguments
import sys

# Import re to use regex on input file
import re

# Import math for calculations in main loop
import math

# Import norm for pdf function
from scipy.stats import norm

# Receive sensor and transition data file names and end time from command line
sensor = open(str(sys.argv[1]), "rt")
transition = open(str(sys.argv[2]), "rt")
# Number of sensor readings to include in calculations before returning answers
ENDTIME = int(sys.argv[3])

# Assign a value for the standard deviation of the sensor readings
STDEV = (2 / 3)

# Read the sensor readings into a 2D array and close input file
readings = re.findall("(\d+),(\d+),(\d+\.\d+),(\d+)", sensor.read())
sensor.close()

# Find the size of the grid and populate a probability map with default values
gridsize = int(readings[0][3])
pDefault = 1 / (gridsize ** 2)
pMap = []
for x in range(gridsize):
    newRow = []
    for y in range(gridsize):
        newRow.append(pDefault)
    pMap.append(newRow)

# Read the transition probabilities into a 2D array and close input file
transition.readline()
pTrans = []
for x in range(gridsize):
    newRow = []
    for y in range(gridsize):
        probs = re.split(",", transition.readline())
        element = [float(probs[2]), float(probs[3]), float(probs[4]), float(probs[5])]
        newRow.append(element)
    pTrans.append(newRow)

# Main calculation loop
hiddenX = 0
hiddenY = 0
time = 0
while time < ENDTIME:
    # Store input values for this time step
    agentX = int(readings[time][0])
    agentY = int(readings[time][1])
    eDist = float(readings[time][2])
    # Initialize a variable for normalization
    pTotal = 0
    # Save a copy of previous pMap values
    pMapOld = pMap.copy()
    # Calculate probabilities for each grid space
    for x in range(gridsize):
        for y in range(gridsize):
            # Find actual distance from agent
            distance = math.sqrt(((x - agentX) ** 2) + ((y - agentY) ** 2))
            # Find the probability of this distance giving this eDist
            pSensor = norm.pdf(eDist, distance, STDEV)
            # Calculate transition*start probability
            pTransNorth = pTrans[(x - 1) % gridsize][y][2] * pMapOld[(x - 1) % gridsize][y]
            pTransEast = pTrans[x][(y + 1) % gridsize][3] * pMapOld[x][(y + 1) % gridsize]
            pTransSouth = pTrans[(x + 1) % gridsize][y][0] * pMapOld[(x + 1) % gridsize][y]
            pTransWest = pTrans[x][(y - 1) % gridsize][1] * pMapOld[x][(y - 1) % gridsize]
            # Calculate probability of the hidden car being in this space
            pMap[x][y] = pSensor * (pTransNorth + pTransEast + pTransSouth + pTransWest)
            # Update normalization variable
            pTotal += pMap[x][y]
    # Normalize the sum of all probabilities to 1
    for x in range(gridsize):
        for y in range(gridsize):
            pMap[x][y] = pMap[x][y] / pTotal
            # Find maximum probability
            if pMap[x][y] > pMap[hiddenX][hiddenY]:
                hiddenX = x
                hiddenY = y
    # Increment time step forward
    time += 1

# Output the data to a file
outName = "pMap_atTime" + str(ENDTIME) + ".csv"
output = open(outName, "w")
output.write("Outputs are arranged as such:\n"
             "(0,0)(0,1)\n"
             "(1,0)(1,1)\n\n")
for x in range(gridsize):
    for y in range(gridsize):
        output.write(str(pMap[x][y]))
        if y < (gridsize - 1):
            output.write(",")
        else:
            output.write("\n")

# Print the most probable location of the hidden car
print("At time " + str(ENDTIME) + ", the hidden car is most likely at: (" + str(hiddenX) + ", " + str(hiddenY) + ")")
print("(%" + str(pMap[hiddenX][hiddenY] * 100) + " chance)")

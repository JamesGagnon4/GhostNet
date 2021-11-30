import sys
import nintaco
import random
from random import randint
import math
import time
import pickle

from GhostState import GhostState

#Use localhost if game is played on the same machine or use IP to use another machine on the network

nintaco.initRemoteAPI("192.168.1.182", 9999)
api = nintaco.getAPI()

STRING = "REWARDS: 00000"
WALKED = "REWARDS: "
PAGE = "PAGE: "
TILE = " TILE: "
STRING_1 = PAGE + TILE

global startTime
global score
global maxScore
global meReward
global maxFit
global reward
WALKED_VAL = 0
maxScore = 0
meReward =0
SPRITE_ID = 123
SPRITE_SIZE = 32
global mapGrid, mapAwards
global rewardArray
global timeArray
global tempX
global action
global episodeCount
global tempValues
global walkedArray, stateID
#tempValues [6960]
global tempCount
global maxAction
global scoreCount
global State
global actionScore
global actionReward
global movePenalty
global floor
floor = 22
movePenalty = 0
actionScore = 0
actionReward =0
State = 0
scoreCount = 0
mapGrid= [[0]*30]*448
walkedArray=[0]*112
rewardArray = [0]*20000
maxAction = [None] * 3584
tempValues = [0] *3584
tempCount = 0
tempX = 0
action = 2

stateID = []
print("Generating State List")

for i in range(112): #X LOCATION
    for j in range(8): #Y LOC
        
        stateID.append((i,j))
        

print("List completed")
print("State Space is "+str(len(stateID)))
# VARIABLES
global epsilon
global alpha
global gamma
epsilon=.2
gamma=0.8
episodeCount=0
alpha = .1
discount = float(gamma)
actionSpace = 3
stateSpace = 225
QValues= []
for i in range(225):
    row = []
    for j in range(actionSpace):
        row.append(0)
    QValues.append(row)



#Initialize QTable with length of 14400 distinct states. Game plays at 60 FPS, allow for 4 minutes of gameplay per episode.
#print QValues

def launch():
  
  api.addControllersListener(gamePad)
  api.addFrameListener(renderFinished)
  api.addStatusListener(statusChanged)
  api.addActivateListener(apiEnabled)
  api.addDeactivateListener(apiDisabled)
  api.addStopListener(dispose)
  api.run()

def apiEnabled():
  global strWidth
  global strWidth1
  global strX
  global strY
  global strX1
  global strY1
  
  api.setSpeed(-1) #highest emulation speed
  #print("They've gone plaid!")

  #print("API enabled")
  strWidth = api.getStringWidth(STRING, False)
  strWidth1 = api.getStringWidth(STRING_1, False)
  strX = (256 - strWidth) / 2 - 50
  strY = 10
  strX1 = (256 - strWidth) / 2 + 50
  strY1 = 10
  
  State = 0
  
def apiDisabled():
  print("API disabled")
def dispose():
  print("API stopped")
  
def statusChanged(message):
  print("Status message: %s" % message)

BoxRadius = 6
InputSize = (BoxRadius*2+1)*(BoxRadius*2+1)

Inputs = InputSize+1
 
#MY FUNCTIONS AND VARIABLES START
#Button Values
ButtonNames = [0, 1, 2, 3, 4, 5]
Outputs = len(ButtonNames)
A = 0
B = 1

Select = 2
Start = 3
Up = 4
Down = 5
Left = 6
Right = 7
true = 1
false = 0

#Explore grid between x1,y1 and x2,y2
#IMPORTANT Y COORDS ARE IN DESCENDING ORDER
def checkMap(x1,y1,x2,y2):
    tempX = 0
    tempY = 0
    
    tempGrid = [[0]*(y1-y2)]*(x2-x1)
    for i in range(x1, x2):
        
        for j in range(y2,y1):
            tempGrid[i-x1][j-y2] = mapGrid[i][j]
            
        
    return tempGrid
def detectCollision():
    if api.readCPU(0x0490) == 0xFE:
        return true      
    

#INPUT METHODS
def pressA():
  api.writeGamepad(0, A, true)
 # print("A  pressed")
 

def pressB():
  api.writeGamepad(0, B, true)
 # print("B  pressed")

def moveUp():
  api.writeGamepad(0, Up, true)
 # print("Up  pressed")

def moveDown():
  api.writeGamepad(0, Down, true)
  #print("Down Pressed")

def moveLeft():
  api.writeGamepad(0, Left, true)
  #print("Left  pressed")

def moveRight():
    api.writeGamepad(0, Right, true)
    #print("Right pressed")
    

def getWalked():
    xWalked = getX()+getPage()*256
    return xWalked

def getX():
    x = api.readCPU(0x0086)
    
    return x

def getY():
    y = api.readCPU(0x00CE)
    
    return  y
def getXVelocity():
   
    speed = api.readCPU(0x0700)
    
    if speed == 0 or speed ==1:
        xVel = 0
        return xVel 
    if speed > 1 and speed <=30:
        xVel =1
        return xVel
    if speed > 30:
        xVel = 2
        return xVel
    
def getXTile():
    x = getWalked()
   
   
    subx = math.floor(x/32)
   
    #priTile =le:", subx)
    return int(subx)

def getYTile():
    y = getY()
    suby = math.floor(y/32)

    return int (suby)

def getEnemyTile():
    enemyX = api.readCPU(0x02DB)
    #print(enemyX)
    enemyTile = math.floor(enemyX/8)
    return enemyTile



def getPage():
    pageNo = api.readCPU(0x006D)
    #print("Page:", pageNo)
    return int(pageNo)

def getScore():
    score = api.readCPU(0x07D8)*100000+api.readCPU(0x07D9)*10000+api.readCPU(0x07DA)*1000+api.readCPU(0x07DB)*100
    return score

def levelComplete():
    completed = false 
    if api.readCPU(0x0178) ==7:
        completed = true
    return completed

def getTime():
    time1s = api.readCPU(0x07FA)
    time10s = api.readCPU(0x07F9)
    time100s = api.readCPU(0x07F8)
    
    time = time1s+time10s*10+time100s*100
    return time
def timeOff():
    api.writeCPU(0x07FA, 255)
    api.writeCPU(0x07F9, 255)
    api.writeCPU(0x07F8, 255)

def detectEnemy():
    enemies =[]
    enemies.append(api.readCPU(0x000F))
    enemies.append(api.readCPU(0x0010))
    enemies.append(api.readCPU(0x0011))
    enemies.append(api.readCPU(0x0012))
    enemies.append(api.readCPU(0x0013))
    
    return enemies

def enemyProx():
    
    #print("enemy Tile is ", enX1)
    
    marioX = api.readCPU(0x04AC)
    enemyX = api.readCPU(0x04B0)
    enemyX1 = api.readCPU(0x04B2)
    enemyX2 = api.readCPU(0x04B4)
    enemyX3 = api.readCPU(0x04B8)
    enemyX4 = api.readCPU(0x04BA)
    d1 = enemyX-marioX
    
    if abs(enemyX - marioX) < 30 or abs (enemyX2 - marioX) <30 or abs (enemyX4 - marioX) < 30 or abs (enemyX3- marioX) < 30 or abs(enemyX1 - marioX) < 30:
        return 1
    else:
        return 0
def enemySide():
    enemy = enemyProx()
    if enemyProx() <0:
        return 0
    if enemyProx()>=0:
        return 1

def enemyDistance(enemies):
    enemyDist = []
    if enemies[0] ==1:
        enemyDist.append(api.readCPU(0x0087)-getX())
        #print(api.readCPU(0x0087)-getX())

    return enemyDist

def xOrientation():
    orient = api.readCPU(0x0045) #1 = right 0 = Left
    return orient


def getReward():
    walked = 0
    flagpole = 0
    score = getScore()
    for i in range(112):
        walked+=walkedArray[i]   
        if walkedArray[102]==1:
            flagpole = 100

    #walked = getWalked()/3 #ultimate goal is to move right, so assign more weight to this goal
    #score = getScore() 
    time = getTime()
    
    reward = (walked)+flagpole+score*0

    return reward

def controller(value):
	
    if value == 0:
        pressA()

    if value == 1:
        moveRight()
        pressA()

    if value == 2:
        moveRight()

    if value ==3:
        moveRight()
        pressA()

    if value ==4:
        moveRight()
        pressB()

    if value ==5:
        moveRight()
        pressB()
        pressA()

def gamePad():
    button = None
    if api.readGamepad(0,0)==true:
        button = 0
    if api.readGamepad(0,1) ==true:
        button = 1
    if api.readGamepad(0,7)==true:
        button = 2
    if api.readGamepad(0,6)==true:
        button = 3
    if api.readGamepad(0,4) ==true:
        button = 4
    if api.readGamepad(0,5)==true:
        button = 5
    return button
 #BEGIN Q LEARNING FUNCTIONS
 #
 #
 #

def getAction(state):
    value = None
    legalMoves = [0,1,2]
    #roll =random.randint(0,1)
    
    if random.random() < epsilon:
        value = random.choice(legalMoves)
       # print("Choosing Random")
               
        return value
        
    else:
        print("chosen from Q")
        value = actionFromQValues(state)

        
        
    return value

def actionFromQValues(state):
    

    action = 2
    value = valueFromQValues(state)
    actions = []

    for action in range (3):
        if value is getQValue(state, action):
          #  print("Q Value of action " +str(action) + " at State " +str(state)+" is " +str(value))
            return action
            
    return action
    

    

def valueFromQValues(state):
    Qval = float('-inf')
    for action in range(3):
        Qval = max(getQValue(state, action), Qval)
        
    if Qval == float('-inf'):
        #print(Qval)
        return 0.0
    else:
        #print(Qval)
        return Qval

def getQValue(state, action):

    return QValues[state][action]


#THIS IS WHERE THE MAGIC HAPPENS!
def update(state, action, nextState, reward):
    QValues[state][action] = (1-alpha) * QValues[state][action] + alpha * (reward + discount*valueFromQValues(nextState))
    print("Updated Value for State "+str(state)+ " and action "+str(action)+ "with reward " +str(reward)+ " is "+str(QValues[state][action]))

update(66, 0,68, 1)


update(84, 0, 88, 1)
update(150, 0,154, 1)


def getPolicy(state):
    return actionFromQValues(state)

def getValue(state):
    return valueFromQValues(state)


def eHeading():
    heading= api.readCPU(0x0046)
    return heading  #1 right, 2 left
def eYTile():
    eY =api.readCPU(0x00CF)
    eYTile = math.floor(eY/8)
    return eYTile

def eYrel():
    val = eYTile()-getYTile()
    if val > 0:   # 0 Below, 1 Even
        return 0
    return 1

def state(): #mheading = xOrientation()
    
    xLoc = getXTile()
    yLoc = getYTile()
    
    enemyLoc = enemyProx()
    sID = xLoc*2+enemyLoc

    #print(sID)
    return sID

def renderFinished():
    global maxScore
    global meReward
    global movePenalty
    global currentFrame
    global episodeCount
   # reward = getReward()+movePenalty
    global tempValues
    global rewardArray
    global timeArray
    global maxAction
    global tempCount
    global scoreCount
    global tempX
    global walkedArray, rewardArray, mapAwards
    global State
    global action
    global actionScore
    global actionReward
    global epsilon, alpha, gamma
    score = getScore()
    tempFrame = 0
    #episodeReward = reward
    episodeScore = score
    reward = getReward()
    STRING_1 = "EPISODE " + str(episodeCount) 
    STRING = WALKED + str(reward)
    api.setColor(nintaco.DARK_BLUE)
    api.fillRect(strX - 1, strY - 1, strWidth + 2, 9)
    api.setColor(nintaco.BLUE)
    api.drawRect(strX - 2, strY - 2, strWidth + 3, 10)
    api.setColor(nintaco.DARK_BLUE)
    api.fillRect(strX1 - 1, strY1 - 1, strWidth1 + 24, 9)
    api.setColor(nintaco.BLUE)
    api.drawRect(strX1 - 2, strY1 - 2, strWidth1 + 25, 10)
    api.setColor(nintaco.WHITE)
    api.drawString(STRING, strX, strY, False)
    api.drawString(STRING_1, strX1, strY1, False)
    currentFrame = api.getFrameCount()
   
    

    fo = open("output.dat", "w+")
    #timeOff()

   
    eStatus = 0
    sx = getXTile()
    goalState = (448*22)
    
    State= state()

    guideCount =-5  #Set to 1 or greater to manually control game input
    eCount =20000
        
    #print(eHeading())
    
    tempCount = 0
    nextState = 5

   


    if (getTime()%10==0):
         tempX = getWalked()
    #TRAINING MODE BEGINS HERE
    if (episodeCount < eCount):

            startTime = 386
            currentTime = getTime()
                  
            timeArray=[0]*eCount
            actionScore = 0
            actionReward = 0

            #MAPPING ROUTINES         

            Walked1 = getWalked()
            Walked = int(math.floor(Walked1/32))
            if(walkedArray[Walked]==0):
                walkedArray[Walked] = 1
           

            
            if episodeCount <= guideCount:
                if gamePad() != None:
                    action = gamePad()
                if gamePad ==None:
                    action = 2
            
            #print(action)
            
            if(currentFrame % 20 ==0): #3 actions per second
                tempCount+=1

                if(episodeCount > guideCount):
                    action = getAction(State)
                    if (api.readCPU(0x0491)==1 ):
                            print("Hit")
                            update(State, action, state(), -1)

               

                distEn = enemyProx()

                if (currentFrame % 480 ==0): #After 8 seconds stuck in a spot, give negative rewards for current action
                    x = getWalked()
                    if x ==tempX:
                        
                        print("Inaction is worse than the wrong action, suffer the penalty for  "+str(action) +" at " +str(State))
                        update(State,action,state(), -1)
                        moveLeft()

            if episodeCount >guideCount:
                controller(action)
                nextState = state()
                if currentFrame % 28 ==0:
                    controller(-1) 

            movePenalty=0

            if(score > maxScore):
                actionScore = score-maxScore

                maxScore = score
                score = 0
                reward+=actionScore
                meReward+=actionScore
            
            else:
                if(currentFrame%20==0):
                    update(State, action, state(), -.1)#Action cost penalty
                    meReward-=1
   
    
    if (api.readCPU(0x000E))==11 or (api.readCPU(0x0712) ==1)or walkedArray[102]==1:

        print("Episode "+str(episodeCount)+ " Reward is "+str(meReward))
        reward = 0
        movePenalty=0
        meReward = 0
        if walkedArray[102]==1:
            update(State, action, state(), 100)
            rewardArray[episodeCount] =1
        walkedArray[102] = 0
        if api.readCPU(0x000E)==11 or api.readCPU(0x0712) ==1:
            update(State, action, state(), -1)
            rewardArray[episodeCount]=-1
        
        api.setSpeed(1)
        api.reset()
        api.loadState("states/MB.save")
        episodeCount+=1

    if episodeCount >= eCount:
        #if episodeCount ==eCount:
           # print("Entering Testing Phase")
        tableOutput = open("Table.txt", "w+")

        for i in range (stateSpace):
            tableOutput.write("\n")
            for j in range(actionSpace):
                tableOutput.write(QValues[i][j])
        
        tableOutput.close()
        State = state()

        if api.readCPU(0x000E)==11:
            api.setSpeed(1)
            api.reset()
            api.loadState("states/MB.save")
            actionCount = 0
        print("Entering testing")

        fo.write("After training " +str(eCount) + "episodes:\n")
        fo.write("Goal met in " +str(actionCount)+" actions")
        for i in range (eCount):
           fo.write(str(i) +" "+str(rewardArray[i])+"\n" )
         #  fo.write(str(i) + " " +str(timeArray[i])+"\n")
        fo.write("Q VALUES\n") 
        for i in range(448):
            for j in range(6):
                fo.write(str(QValues[i][j])+" ")
if __name__ == "__main__":
     launch()

import sys
import nintaco
import random
from random import randint
import math


#Use localhost if game is played on the same machine or use IP to use another machine on the network

nintaco.initRemoteAPI("192.168.1.182", 9999)
api = nintaco.getAPI()

STRING = "REWARDS: 00000"
WALKED = "REWARDS: "
PAGE = "PAGE: "
TILE = " TILE: "
STRING_1 = PAGE + TILE

global maxFit
global rewardi
WALKED_VAL = 0
maxScore = 0

SPRITE_ID = 123
SPRITE_SIZE = 32



def launch():

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

  api.setSpeed(0) #maximum emulation speed
  print("They've gone plaid!")

  print("API enabled")
  strWidth = api.getStringWidth(STRING, False)
  strWidth1 = api.getStringWidth(STRING_1, False)
  strX = (256 - strWidth) / 2 - 50
  strY = 10
  strX1 = (256 - strWidth) / 2 + 50
  strY1 = 10
  
  
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
ButtonNames = ["A", "B", "Up", "Down", "Left", "Right"]
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


#INPUT METHODS
def pressA():
  api.writeGamepad(0, A, true)
  print("A  pressed")
 

def pressB():
  api.writeGamepad(0, B, true)
  print("B  pressed")

def moveUp():
  api.writeGamepad(0, Up, true)
  print("Up  pressed")

def moveDown():
  api.writeGamepad(0, Down, true)
  print("Down Pressed")

def moveLeft():
  api.writeGamepad(0, Left, true)
  print("Left  pressed")

def moveRight():
    api.writeGamepad(0, Right, true)
    print("Right pressed")

def getWalked():
    
    x = api.readCPU(0x0064)
    x2 = api.readCPU(0x0065)*255
    return x+x2
def getX():
    x = api.readCPU(0x05AF)
    return x

def getY():
    y = api.readCPU(0x0599)
    
    return  y

def getTile():
    x = api.getCameraX()
    y = getY()-16
   
    subx = math.floor(x/8)
    suby = math.floor((y-32)/16)
    #print("tile:", subx)
    return int(subx)

def getPage():
    x = getWalked()
    pageNo = math.floor(x/512)
    #print("Page:", pageNo)
    return int(pageNo)

def getScore():
    sc1 = api.readCPU(0x06E8) #100s
    sc2 = api.readCPU(0x06E6) #1000s
    sc3 = api.readCPU(0x06E4) #10000s
        
    if sc1 ==255:  #Score bytes initialize to 255 and need to be zeroed before display
        sc1 = 0
    if sc2 == 255:
        sc2 = 0
    if sc3 == 255:
        sc3 = 0
        
    score = (sc1*100)+(sc2*1000)+(sc3*10000)
    #print(score) 
    return score
def levelComplete():
    completed = false 
    if api.readCPU(0x0178) ==7:
        completed = true
    return completed

def getTime():
    t1 = api.readCPU(0x06FC) #1S
    t2 = api.readCPU(0x06FA) #10s
    t3 = api.readCPU(0x06F6) #Minutes

    time = t1 + (t2*10) + (t3*60) #time in seconds

    return time

def detectEnemy():
    enemies = {}
    for slot in range(0,7):
        enemy = api.readCPU(0x22E)
        if enemy != 0:

            ex = api.readCPU(515 + slot*4*6)
            ey = api.readCPU(0x200 + slot*4*6)
         #   enemies[len(enemies)] = {"x": ex, "y": (ey)}
            if ex != 255 and  ey != 255 and  abs(ey-getY())<48 and  abs(ex-getX())>16 and (ex <120 or ex >130):
                #ex = api.readCPU(515 + slot*4*6)
                #ey = api.readCPU*0x200 + slot*4*6+12)
                enemies[len(enemies)]={"x": ex, "y": ey}
            
               # print(abs(ey-getY()))
                api.drawRect(ex,ey-12, 16,32)
                api.drawLine(126, getY(),ex,ey+12)

    return enemies

def enemyDistance():
    enemies = detectEnemy()
    enemyDist = {}
    for i in range(0, len(enemies)):
        distx = abs(enemies[i]["x"] - getX())
        disty = abs(enemies[i]["y"] - getY())
        enemyDist[len(enemyDist)]={"x": distx, "y": disty}

        if disty < 32:
            api.drawLine(126, getY(), enemies[i]["x"], enemies[i]["y"])
            api.drawRect(enemies[i]["x"], enemies[i]["y"]-12, 16, 32)

    return enemyDist

def getReward():
    walked = getWalked()/3 #ultimate goal is to move right, so assign more weight to this goal
    score = getScore()/10  
    time = getTime()
    timeScore = 10*(120 - time) #lose 10 points of reward for every second lost.

    reward = score+walked-timeScore

    return reward
  
    
def randomCommand():
    buttonList = ['A'] * 50 + ['B'] * 50 + ['Up'] * 10 + ['Down'] * 10 + ['Left'] * 5 + ['Right'] * 90
    #value = 5
    value =  random.choice(buttonList)
    #print(value)
    #value =  random.choices(buttonList, weights=(20, 20, 10, 10, 5, 55), k=1)
    #value = randint(0, 5)
    if value == 'A':
        pressA()
    if value == 'B':
        pressB()
    if value == 'Up':
        moveUp()
    if value == 'Down':
        moveDown()
    if value == 'Left':
        moveLeft()
    if value == 'Right':
        moveRight()



def renderFinished():
    global maxScore    
    reward = getReward()
    if reward > maxScore:
        maxScore = reward
        print("Maximum is", maxScore)

    if levelComplete() ==true:
        maxScore+=99999999
        print("Maximum is", maxScore)
        #api.writeGamepad(0, Start, true)

    #detectEnemy()
    enemyDistance()
    
    STRING_1 = (PAGE + str(getPage()))+ (TILE + str(getTile())) 
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
    #print("CPU is ", api.readOAM(20))
    
    
#ENTER RANDOM COMMAND FOR TESTING
    
    randomCommand()
    #moveRight()
    if api.readCPU(0x0715)==2: #START WITH 3 LIVES, IF WE DIE, RESTART AT BEGINNING STATE.
        reward-=500 #placeholder punishment value
        api.setSpeed(1)
        
        #api.reset()
        api.loadState("states/G&G.save")
        #api.setSpeed(0) #Set emulation levels to maximum speed. 
        WALKED_VAL = 0    #RESET FITNESS TO 0 due to death.
        #apiEnabled()
        #launch()
       
   
if __name__ == "__main__":
  launch()

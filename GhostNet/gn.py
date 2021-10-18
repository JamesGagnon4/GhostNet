import sys
import nintaco
from random import seed
from random import randint

#Use localhost if game is played on the same machine or use IP to use another machine on the network

nintaco.initRemoteAPI("192.168.1.182", 9999)
api = nintaco.getAPI()

STRING = "FITNESS: 00000"
WALKED = "FITNESS: "
STRING_1 = "Gen: 1 Mutation: A"
global maxFit
WALKED_VAL = 0
maxFit = 0

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

def detectEnemy():
    enemies = {}
    for slot in range(0,7):
        enemy = api.readCPU(0x22E)
        if enemy != 0:

            ex = api.readCPU(515 + slot*4*6)
            ey = api.readCPU(0x200 + slot*4*6)
            enemies[len(enemies)] = {"x": ex, "y": ey}
            #if ex != 255 and  ey != 255 and  abs(ey-getY())<48 and  abs(ex-getX())>16 and (ex <120 or ex >130):
            
               # print(abs(ey-getY()))
             #   api.drawRect(ex,ey-12, 16,32)
              #  api.drawLine(126, getY(),ex,ey-12)

    return enemies

def getInputs():
    enemies = detectEnemy()
    inputs = []
    for dy in range(-BoxRadius*16, BoxRadius*16 +1, 16):
        for dx in range(-BoxRadius*16, BoxRadius*16+1, 16):
            inputs[len(inputs)] = 0
            
            for i in range(0, len(enemies)):
                distx = abs(enemies[i]["x"] - (getX()+dx))
                disty = abs(enemies[i]["y"] - (getY()+dy))

                if distx <=8 and disty <=8:
                    inputs[len(inputs)] = -1
    return inputs

    #ZOMBIE DETECTOR
    #if api.readCPU(0x025E)!=0:
        #print("Zombie Detected!")
     #   api.drawRect(api.readCPU(0x0203),api.readCPU(0x0220)-12, 16, 32)
    #CROW DETECT
    #if api.readCPU(0x022E)!=0:
    #    api.drawRect(api.readCPU(0x006A), api.readCPU(0x0238), 16, 32)
    #SATAN DETECT
    #if api.readCPU(0x022E)!=0:
    #    api.drawRect(api.readCPU(0x0233+8), api.readCPU(0x0220),16, 24)

    #FIRST BOSS DETECT
    #if api.readCPU(0x023A)!=0:
    #    api.drawRect(api.readCPU(0x020F),api.readCPU(0x03FC),32,40)

    
def randomCommand():
    value = randint(0, 7)
    if value == 0:
        pressA()
    if value == 1:
        pressB()
    if value == 2:
        print("select pressed")
    if value == 3:
        print("start pressed")
    if value == 4:
        moveUp()
    if value == 5:
        moveDown()
    if value == 6:
        moveLeft()
    if value == 7:
        moveRight()



def renderFinished():
    global maxFit
    tempX = getWalked()
    WALKED_VAL =tempX/3
    #calcDist()
    detectEnemy()
    if WALKED_VAL > maxFit:
        maxFit = WALKED_VAL
       # print("maxFit is ", maxFit)

    STRING = WALKED + str(WALKED_VAL)
    api.setColor(nintaco.DARK_BLUE)
    api.fillRect(strX - 1, strY - 1, strWidth + 2, 9)
    api.setColor(nintaco.BLUE)
    api.drawRect(strX - 2, strY - 2, strWidth + 3, 10)
    api.setColor(nintaco.DARK_BLUE)
    api.fillRect(strX1 - 1, strY1 - 1, strWidth1 + 2, 9)
    api.setColor(nintaco.BLUE)
    api.drawRect(strX1 - 2, strY1 - 2, strWidth1 + 3, 10)
    api.setColor(nintaco.WHITE)
    api.drawString(STRING, strX, strY, False)
    api.drawString(STRING_1, strX1, strY1, False)
    currentFrame = api.getFrameCount()
    #print("CPU is ", api.readOAM(20))
    
    
#ENTER RANDOM COMMAND FOR TESTING
    
    #randomCommand()
    #moveRight()
    if api.readCPU(0x0715)==2: #START WITH 3 LIVES, IF WE DIE, RESTART AT BEGINNING STATE.
        api.setSpeed(1)
        
        api.reset()
    
        api.loadState("states/G&G.save")
        #api.quickLoadState(1)
        #api.setSpeed(100)     
        WALKED_VAL = 0    #RESET FITNESS TO 0 due to death.
        #apiEnabled()
        #launch()
       
   
if __name__ == "__main__":
  launch()

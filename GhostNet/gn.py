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
  sprite = [0 for i in range(SPRITE_SIZE * SPRITE_SIZE)]
  for y in range(SPRITE_SIZE):
	Y = y - SPRITE_SIZE / 2 + 0.5
	for x in range(SPRITE_SIZE):
		X = x - SPRITE_SIZE / 2 + 0.5
		sprite[SPRITE_SIZE * y + x] = nintaco.ORANGE if (X * X + Y * Y 
					<= SPRITE_SIZE * SPRITE_SIZE / 4) else -1
  api.createSprite(SPRITE_ID, SPRITE_SIZE, SPRITE_SIZE, sprite)


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


#MY FUNCTIONS AND VARIABLES START
#Button Values
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

def getX():
    
    x = api.readCPU(0x0064)
    x2 = api.readCPU(0x0065)*255
    return x+x2

def getY():
    y = api.readCPU(0x0200)
    y2 = api.readCPU(0x0204)
    return  y2-y

def detectEnemy():
    #ZOMBIE DETECTOR
    if api.readCPU(0x025E)!=0:
        #print("Zombie Detected!")
        api.drawRect(api.readCPU(0x0203),api.readCPU(0x0220)-12, 16, 32)
    #CROW DETECT
    if api.readCPU(0x022E)!=0:
        api.drawRect(api.readCPU(0x006A), api.readCPU(0x0238), 16, 32)
    #SATAN DETECT
    if api.readCPU(0x022E)!=0:
        api.drawRect(api.readCPU(0x0233+8), api.readCPU(0x0220),16, 24)

    #FIRST BOSS DETECT
    if api.readCPU(0x023A)!=0:
        api.drawRect(api.readCPU(0x020F),api.readCPU(0x03FC),32,40)

    
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
    tempX = getX()
    WALKED_VAL =tempX/3
    detectEnemy()

    if WALKED_VAL > maxFit:
        maxFit = WALKED_VAL
        print("maxFit is ", maxFit)

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
    
    
#ENTER RANDOM COMMAND FOR TESTING
    
    #randomCommand()
    #moveRight()
    #if api.readCPU(0x0715)==2: #START WITH 3 LIVES, IF WE DIE, RESTART AT BEGINNING STATE.
        #api.quickLoadState(1)
      
        # api.loadState("states/G&G.save")i
        #WALKED_VAL = 0    #RESET FITNESS TO 0 due to death.
        
       
   
if __name__ == "__main__":
  launch()

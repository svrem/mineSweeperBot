from PIL import ImageGrab
import numpy as np
import cv2
import pyautogui
import time
import random

time.sleep(2)
try:
    BEGIN_IMAGE = pyautogui.locateOnScreen('empty.png')
except: 
    print('Could\'t find board.')
    exit()
BEGIN = (BEGIN_IMAGE.left,BEGIN_IMAGE.top)
boardLengths = (16  ,16) # x=y y=x

pyautogui.PAUSE = 0.001

past = 1000000000000000000000
did_nothing = 0

tiles = {
   48384: '?',
   41818: '1',
   46338: '0',
   38733: '2',
   32049: 'b',
   41506: 'f',
   36418: '3', 
   34088: '5', 
   37826: '4',
   9009: "cb",
   40578: '6'
}

def removeFromArray(item, array):
    
    if (item in array):
        array.remove(item)
    return array

def getSurround(x,y,board):
    surrounds = [[-1,-1], [0,-1], [1,-1], 
                 [-1,0], [1,0],
                 [-1,1], [0,1], [1,1] ]
    
    if (x == 0):            
        removeFromArray([-1,-1],surrounds)
        removeFromArray([-1,0],surrounds)
        removeFromArray([-1,1],surrounds)
    if (x == boardLengths[0]-1):
        removeFromArray([1,-1],surrounds)
        removeFromArray([1,0],surrounds)
        removeFromArray([1,1],surrounds)
    if (y == 0):
        removeFromArray([0,-1],surrounds)
        removeFromArray([-1,-1],surrounds)
        removeFromArray([1,-1],surrounds)
    if (y == boardLengths[1]-1):
        removeFromArray([-1,1],surrounds)
        removeFromArray([0,1],surrounds)
        removeFromArray([1,1],surrounds)
    
    surroundNumbers = []
    positions = []
 
    for surround in surrounds:
        surroundNumbers.append(board[y+surround[1], x+surround[0]])
        positions.append([x+surround[0], y+surround[1]])
        
        
    return {'surroundNumbers': surroundNumbers, 'positions': positions}

def clickTile(x,y, typeClick):
    print(x,y,typeClick)
    pyautogui.click(BEGIN[0]+8+(x*16),BEGIN[1]+8+(y*16), button=typeClick, duration=0)
    
def simple_calc(board, presses):
    global did_nothing
    
    past = 0
    for x in range(boardLengths[1]):
        for y in range(boardLengths[0]):
            surrounds = getSurround(x,y,board)
            tileIsNumber = False

            try: 
                int(board[y,x])
                tileIsNumber = True
            except: pass

            if tileIsNumber and board[y, x] != '0':
                if int(board[y,x]) != 0 and surrounds['surroundNumbers'].count('?')+surrounds['surroundNumbers'].count('f') == int(board[y,x]):
                    for i, surround in enumerate(surrounds['surroundNumbers']):
                        if surround == '?' and surrounds['positions'][i] not in presses :
                            presses.append(surrounds['positions'][i])
                            past += 1
                                
                            clickTile(surrounds['positions'][i][0],surrounds['positions'][i][1], 'right')
                            board[surrounds['positions'][i][1],surrounds['positions'][i][0]] = 'f'
                if (surrounds['surroundNumbers'].count('f') == int(board[y,x]) and surrounds['surroundNumbers'].count('?') > 0  ):
                    clickTile(x,y, 'middle')
                    past += 1
    if past == 0: 
        did_nothing += 1
    else:
        did_nothing = 0

def reset():
    global did_nothing
    did_nothing = 0
    clickTile(boardLengths[0]//2, -2, 'left')
    
    time.sleep(1)
    
    clickTile(boardLengths[0]//2, boardLengths[1]//2, 'left')    
    time.sleep(.1)   
    pyautogui.mouseUp()
                
def analyze(first):
    global past,did_nothing


    board = np.zeros((boardLengths[1], boardLengths[0]), str)

    board_img =  cv2.cvtColor(np.array(ImageGrab.grab((BEGIN[0],BEGIN[1],BEGIN[0]+16*boardLengths[0], BEGIN[1]+16*boardLengths[1]))), cv2.COLOR_BGR2GRAY)

    for y in range(0,len(board_img),16):
        for x in range(0,len(board_img[y]),16):
            summer = board_img[y:y+16, x:x+16].sum()
            if summer in tiles:
                if tiles[summer] == 'cb':
                    time.sleep(2)
                    reset()
                    return
                board[y//16,x//16 ] = tiles[summer]
            else:
                # print(s ummer)
                cv2.imshow('',board_img[y:y+16, x:x+16])
                print(f'Couldn\'t find tile by image. Look at the image and correct the number in the tiles dictionary. This number should be {summer}!')
                cv2.waitKey(0)
    if ('?' not in board):
        print('ez')
        time.sleep(3)
        reset()
        
        
        
    if did_nothing < 3:
        presses = []

        simple_calc(board, presses)
    else:
        print('random move')
        did_nothing = 0
        chance_board = np.zeros((boardLengths[0],boardLengths[1]))
        
        for y in range(len(board)):
            for x in range(len(board[y])):
                
                isInt = False
                try: 
                    int(board[y,x])
                    isInt = True    
                except:
                    pass
                if (isInt):
                    surrounds = getSurround(x,y,board)
                    num_needed = int(board[y,x])-surrounds['surroundNumbers'].count('f')
                    
                    
                    if num_needed != 0:
                        weight = num_needed/surrounds['surroundNumbers'].count('?')
                        for i,surround in enumerate(surrounds['surroundNumbers']):
                            if surround == '?':
                                chance_board[surrounds['positions'][i][1],surrounds['positions'][i][0]] += weight 
                    else:
                        chance_board[y,x] += -100
                        
        lowest = [[0,0], 101] 
        highest = [[0,0], -101]        
        for y in range(len(chance_board)):
            for x in range(len(chance_board[y])):   
                if chance_board[y,x] > highest[1] and board[y,x] == '?':
                    highest[1] = chance_board[y,x]
                    highest[0] = [x,y]
                elif chance_board[y,x] < lowest[1] and board[y,x] == '?' and  chance_board[y,x] != 0:
                    lowest[1] = chance_board[y,x]
                    lowest[0] = [x,y]
        clickTile(highest[0][0],highest[0][1], 'right')
        # clickTile(lowest[0][0],lowest[0][1], 'left')
        # print(chance_board)
        # exit()
                
                    
                
                
            
        
        

reset()        


# clickTile(boardLengths[0]//2, boardLengths[1]//2, 'left')    
# time.sleep(.001)          
first = True
while True:
    analyze(first)
    first = False


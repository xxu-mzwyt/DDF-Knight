import random, sys, copy, os, pygame, time
from pygame.locals import *

# 初始化
FPS = 60
# 窗口与方块尺寸
win_wid = 1366
win_hei = 768
blo_wid = 50
blo_hei = 85
blo_hei_floor = 40

cam_spe = 5
global isAttacking
BGCOLOR = (0, 0, 0)
TEXTCOLOR  = (255, 255, 255)
getDamage = False
LeftSide = False
isAttacking = False
Dead = False

'''hitplayer = pygame.mixer.Sound('hitplayer.wav')
hitenemy = pygame.mixer.Sound('hitenemy.wav')
spawnenemy = pygame.mixer.Sound('spawnenemy.wav')'''

def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage, YourTurn, getDamage, sleeptime

    # Pygame initialization and basic set up of the global variables.
    # 
    #
    #  
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.mixer.init()
    backsound=pygame.mixer.Sound('sound.wav')
    backsound2=pygame.mixer.Sound('ACT2.ogg')

    random.choice([backsound2,backsound]).play(-1)
    # Because the Surface object stored in DISPLAYSURF was returned
    # from the pygame.display.set_mode() function, this is the
    # Surface object that is drawn to the actual computer screen
    # when pygame.display.update() is called.
    DISPLAYSURF = pygame.display.set_mode(((win_wid, win_hei)),FULLSCREEN)

    pygame.display.set_caption(random.choice(['DDF_Knight:你还想活下去？',
                                              'DDF_Knight:头发的哭泣',
                                              'DDF_Knight:直至键盘崩溃',
                                              'DDF_Knight:或许有更糟的',
                                              'DDF_Knight:为什么是人工智障？']))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)

    # A global dict value that will contain all the Pygame
    # Surface objects returned by pygame.image.load().
    IMAGESDICT = {'uncovered goal': pygame.image.load('RedSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'barrier': pygame.image.load('barrier.png'),
                  'corner': pygame.image.load('Wall_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'knight': pygame.image.load('knight.png'),
                  'lord': pygame.image.load('lord.png'),
                  'shieldman': pygame.image.load('shieldman.png'),
                  'soldier': pygame.image.load('soldier.png'),
                  'sword': pygame.image.load('sword.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png'),
                  'yourturn': pygame.image.load('yourturn.png'),
                  'enemyturn': pygame.image.load('enemyturn.png'),
                  'knightL': pygame.image.load('knightL.png'),
                  'knight_attack': pygame.image.load('knight_attack.png'),
                  'knight_attackL': pygame.image.load('knight_attackL.png'),
                  'knight_hurted': pygame.image.load('knight_hurted.png'),
                  'knight_hurtedL': pygame.image.load('knight_hurtedL.png'),
                  'soldierL': pygame.image.load('soldierL.png'),
                  'soldier_attack': pygame.image.load('soldier_attack.png'),
                  'soldier_attackL': pygame.image.load('soldier_attackL.png'),
                  'soldier_die': pygame.image.load('soldier_die.png'),
                  'soldier_dieL': pygame.image.load('soldier_dieL.png'),
                  'died': pygame.image.load('died.png'),
                  'yeah': pygame.image.load('yeah.png')}



    # These dict values are global, and map the character that appears
    # in the level file to the Surface object it represents.
    TILEMAPPING = {'x': IMAGESDICT['corner'],
                   '#': IMAGESDICT['wall'],
                   'o': IMAGESDICT['inside floor'],
                   ' ': IMAGESDICT['outside floor']}
    OUTSIDEDECOMAPPING = {'1': IMAGESDICT['rock'],
                          '2': IMAGESDICT['short tree'],
                          '3': IMAGESDICT['tall tree'],
                          '4': IMAGESDICT['ugly tree']}

    # PLAYERIMAGES is a list of all possible characters the player can be.
    # currentImage is the index of the player's current player image.
    currentImage = 0
    PLAYERIMAGES = [IMAGESDICT['knight'],
                    IMAGESDICT['knightL'],
                    IMAGESDICT['knight_attack'],
                    IMAGESDICT['knight_attackL'],
                    IMAGESDICT['knight_hurted'],
                    IMAGESDICT['knight_hurtedL'],
                    IMAGESDICT['soldier'],
                    IMAGESDICT['soldierL'],
                    IMAGESDICT['soldier_attack'],
                    IMAGESDICT['soldier_attackL'],
                    IMAGESDICT['soldier_die'],
                    IMAGESDICT['soldier_dieL'],
                    IMAGESDICT['sword'],
                    IMAGESDICT['yeah']]

    startScreen() # show the title screen until the user presses a key

    # Read in the levels from the text file. See the readLevelsFile() for
    # details on the format of this file and how to make your own levels.
    levels = readLevelsFile('DDFlevel.txt')
    currentLevelIndex = 0

    # The main game loop. This loop runs a single level, when the user
    # finishes that level, the next/previous level is loaded.
    while True: # main game loop
        # Run the level to actually start playing the game:
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):
            # Go to the next level.
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                # If there are no more levels, go back to the first one.
                currentLevelIndex = 0
        elif result == 'back':
            # Go to the previous level.
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                # If there are no previous levels, go to the last one.
                currentLevelIndex = len(levels)-1
        elif result == 'reset':
            pass # Do nothing. Loop re-calls runLevel() to reset the level



def runLevel(levels, levelNum):
    global currentImage, getDamage, YourTurn, SolList, health, MAXHEALTH, score, LeftSide, getDamage, keyPressed
    SolList=[]
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True # set to True to call drawMap()
    #levelSurf = BASICFONT.render('Level %s of %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    #levelRect = levelSurf.get_rect()
    #levelRect.bottomleft = (20, win_hei - 35)
    mapWidth = len(mapObj) * blo_wid
    mapHeight = (len(mapObj[0]) - 1) * blo_hei_floor + blo_hei
    MAX_CAM_X_PAN = abs(int(win_hei / 2) - int(mapHeight / 2)) + blo_wid
    MAX_CAM_Y_PAN = abs(int(win_wid / 2) - int(mapWidth / 2)) + blo_hei

    YourTurn = True
    getDamage = False
    levelIsComplete = False
    # Track how much the camera has moved:
    cameraOffsetX = 0
    cameraOffsetY = 0
    # Track if the keys to move the camera are being held down:
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False
    health = 5
    MAXHEALTH=5
    score = 0
    while True: # main game loop        # Reset these variables:

        sleeptime=0
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                # Player clicked the "X" at the corner of the window.
                terminate()

            elif event.type == KEYDOWN:
                # Handle key presses
                keyPressed = True
                if levelIsComplete == False:
                    if event.key == K_LEFT:
                        if YourTurn == True:
                            playerMoveTo = 'left'
                            LeftSide = True
                    elif event.key == K_RIGHT:
                        if YourTurn == True:
                            playerMoveTo = 'right'
                            LeftSide = False
                    elif event.key == K_UP:
                        if YourTurn == True:
                            playerMoveTo = 'up'
                    elif event.key == K_DOWN:
                        if YourTurn == True:
                           playerMoveTo = 'down'

                # Set the camera move mode.
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                    mapNeedsRedraw = True

                #elif event.key == K_n:
                #    return 'next'
                #elif event.key == K_b:
                #    return 'back'

                if event.key == K_ESCAPE:
                    terminate() # Esc key quits.
                if event.key == K_r:
                    return 'reset' # Reset the level.

            elif event.type == KEYUP:
                # Unset the camera move mode.
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo != None and not levelIsComplete:    

            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved:
                # increment the step counter.
                YourTurn = False
                pygame.display.update()
                # time.sleep(0.5)

                for soldier in range(len(SolList)):
                    dire = random.randint(1,5)
                    if dire == 1 and not isWall(mapObj,SolList[soldier][0] - 1,SolList[soldier][1]) and not (SolList[soldier][0] - 1,SolList[soldier][1]) in SolList and not (SolList[soldier][0] - 1,SolList[soldier][1])==gameStateObj['player']:
                        SolList[soldier] = (SolList[soldier][0] - 1,SolList[soldier][1])
                    if dire == 2 and not isWall(mapObj,SolList[soldier][0] + 1,SolList[soldier][1]) and not (SolList[soldier][0] + 1,SolList[soldier][1]) in SolList and not (SolList[soldier][0] + 1,SolList[soldier][1])==gameStateObj['player']:
                        SolList[soldier] = (SolList[soldier][0] + 1, SolList[soldier][1])
                    if dire == 3 and not isWall(mapObj,SolList[soldier][0],SolList[soldier][1] - 1) and not (SolList[soldier][0],SolList[soldier][1] - 1) in SolList and not (SolList[soldier][0],SolList[soldier][1] - 1)==gameStateObj['player']:
                        SolList[soldier] = (SolList[soldier][0], SolList[soldier][1] - 1)
                    if dire == 4 and not isWall(mapObj,SolList[soldier][0],SolList[soldier][1] + 1) and not (SolList[soldier][0],SolList[soldier][1] + 1) in SolList and not (SolList[soldier][0],SolList[soldier][1] + 1)==gameStateObj['player']:
                        SolList[soldier] = (SolList[soldier][0], SolList[soldier][1] + 1)
                for soldier in range(len(SolList)):
                    if gameStateObj['player'][0] == SolList[soldier][0] - 1 and gameStateObj['player'][1] == SolList[soldier][1]:
                        health -=1
                        getDamage = True
                    if gameStateObj['player'][0] == SolList[soldier][0] + 1 and gameStateObj['player'][1] == SolList[soldier][1]:
                        health -=1
                        getDamage = True
                    if gameStateObj['player'][0] == SolList[soldier][0] and gameStateObj['player'][1] == SolList[soldier][1] - 1:
                        health -= 1
                        getDamage = True
                    if gameStateObj['player'][0] == SolList[soldier][0] and gameStateObj['player'][1] == SolList[soldier][1] + 1:
                        health -=1
                        getDamage = True


                if len(SolList) <= 10:

                    if random.randint(1,15) == 1 and not (1,1) in SolList:
                        SolList.append((1, 1))
                        #spawnenemy.play()
                    if random.randint(1, 15) == 1 and not (25,1) in SolList:
                        SolList.append((25, 1))
                        #spawnenemy.play()
                    if random.randint(1,15) == 1 and not (1,15) in SolList:
                        SolList.append((1, 15))
                        #spawnenemy.play()
                    if random.randint(1,15) == 1 and not (24,15) in SolList:
                        SolList.append((24, 15))
                        #spawnenemy.play()

                gameStateObj['soldier'] = SolList


                YourTurn = True
            if isLevelFinished():
                # level is solved, we should show the "Solved!" image.
                levelIsComplete = True
                keyPressed = False

        DISPLAYSURF.fill(BGCOLOR)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            #mapNeedsRedraw = False



        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += cam_spe
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= cam_spe
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += cam_spe
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= cam_spe

        # Adjust mapSurf's Rect object based on the camera offset.
        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (int(win_wid / 2) + cameraOffsetX, int(win_hei / 2) + cameraOffsetY)

        # Draw mapSurf to the DISPLAYSURF Surface object.
        DISPLAYSURF.blit(mapSurf, mapSurfRect)
        drawHealthMeter(health)
        font = pygame.font.SysFont("calibri", 40)
        score2 = font.render(str(score), True, (100, 100, 255))
        DISPLAYSURF.blit(score2, (1300., 10.))
        # BACICFONT = pygame.font.Font('zhaozi.ttf', 30)
        # text =BASICFONT.render(score, 1, (0,0,0))
        # DISPLAYSURF.blit(text, (280, 100))
        #DISPLAYSURF.blit(levelSurf, levelRect)
        #stepSurf = BASICFONT.render('Steps: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
        #stepRect = stepSurf.get_rect()
        #stepRect.bottomleft = (20, win_hei - 10)
        #DISPLAYSURF.blit(stepSurf, stepRect)

        if levelIsComplete:
            # is solved, show the "Solved!" image until the player
            # has pressed a key.
            solvedRect = IMAGESDICT['solved'].get_rect()
            solvedRect.center = (int(win_wid / 2), int(win_hei / 2))
            DISPLAYSURF.blit(IMAGESDICT['solved'], solvedRect)
            if keyPressed:
                return 'solved'




        pygame.display.update() # draw DISPLAYSURF to the screen.
        FPSCLOCK.tick()

def drawHealthMeter(currentHealth):
    global keyPressed, Dead
    for i in range(currentHealth): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, (255,0,0),   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, (0,0,0), (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)
    if currentHealth <= 0:
        # is solved, show the "Solved!" image until the player
        # has pressed a key.
        solvedRect = IMAGESDICT['died'].get_rect()
        solvedRect.center = (int(win_wid / 2), int(win_hei / 2))
        DISPLAYSURF.blit(IMAGESDICT['died'], solvedRect)
        Dead = True
        if keyPressed:
            return 'reset'



def isWall(mapObj, x, y):
    """Returns True if the (x, y) position on
    the map is a wall, otherwise return False."""
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False # x and y aren't actually on the map.
    elif mapObj[x][y] in ('#', 'x','*'):
        return True # wall is blocking
    return False


def decorateMap(mapObj, startxy):
    """Makes a copy of the given map object and modifies it.
    Here is what is done to it:
        * Walls that are corners are turned into corner pieces.
        * The outside/inside floor tile distinction is made.
        * Tree/rock decorations are randomly added to the outside tiles.

    Returns the decorated map object."""

    startx, starty = startxy # Syntactic sugar

    # Copy the map object so we don't modify the original passed
    mapObjCopy = copy.deepcopy(mapObj)

    # Remove the non-wall characters from the map data
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    # Flood fill to determine inside/outside floor tiles.
    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    # Convert the adjoined walls into corner tiles.
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or \
                   (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or \
                   (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or \
                   (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < 20:
                mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    """Returns True if the (x, y) position on the map is
    blocked by a wall or barrier, otherwise return False."""

    if isWall(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True # x and y aren't actually on the map.

    elif (x, y) in gameStateObj['barriers']:
        return True # a barrier is blocking

    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):
    global score, isAttacking
    """Given a map and game state object, see if it is possible for the
    player to make the given move. If it is, then change the player's
    position (and the position of any pushed barrier). If not, do nothing.

    Returns True if the player moved, otherwise False."""

    # Make sure the player can move in the direction they want.
    playerx, playery = gameStateObj['player']

    # This variable is "syntactic sugar". Typing "barriers" is more
    # readable than typing "gameStateObj['barriers']" in our code.
    barriers = gameStateObj['barriers']

    # The code for handling each of the directions is so similar aside
    # from adding or subtracting 1 to the x/y coordinates. We can
    # simplify it by using the xOffset and yOffset variables.
    if playerMoveTo == 'up':
        xOffset = 0
        yOffset = -1
        if (gameStateObj['player'][0],gameStateObj['player'][1] - 2) in SolList:
            SolList.remove((gameStateObj['player'][0],gameStateObj['player'][1] - 2))
            isAttacking = True
            score += 1
        if (gameStateObj['player'][0],gameStateObj['player'][1] - 1) in SolList:
            SolList.remove((gameStateObj['player'][0],gameStateObj['player'][1] - 1))
            isAttacking = True
            score += 1
    elif playerMoveTo == 'right':
        xOffset = 1
        yOffset = 0
        if (gameStateObj['player'][0] + 2,gameStateObj['player'][1]) in SolList:
            SolList.remove((gameStateObj['player'][0] + 2,gameStateObj['player'][1]))
            score += 1
            isAttacking = True
        if (gameStateObj['player'][0] + 1,gameStateObj['player'][1]) in SolList:
            SolList.remove((gameStateObj['player'][0] + 1,gameStateObj['player'][1]))
            score += 1
            isAttacking = True
    elif playerMoveTo == 'down':
        xOffset = 0
        yOffset = 1
        if (gameStateObj['player'][0],gameStateObj['player'][1] + 2) in SolList:
            SolList.remove((gameStateObj['player'][0],gameStateObj['player'][1] + 2))
            score += 1
            isAttacking = True
        if (gameStateObj['player'][0],gameStateObj['player'][1] + 1) in SolList:
            SolList.remove((gameStateObj['player'][0],gameStateObj['player'][1] + 1))
            score += 1
            isAttacking = True
    elif playerMoveTo == 'left':
        xOffset = -1
        yOffset = 0
        if (gameStateObj['player'][0] - 2,gameStateObj['player'][1]) in SolList:
            SolList.remove((gameStateObj['player'][0] - 2,gameStateObj['player'][1]))
            score += 1
            isAttacking = True
        if (gameStateObj['player'][0] - 1,gameStateObj['player'][1]) in SolList:
            SolList.remove((gameStateObj['player'][0] - 1,gameStateObj['player'][1]))
            score += 1
            isAttacking = True
        # pygame.transform.flip(mapSurf, xbool, ybool)
        # See if the player can move in that direction.
    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in barriers:
            return False
        # Move the player upwards.
        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True



def startScreen():
    """Display the start screen (which has the title and instructions)
    until the player presses a key. Returns None."""

    # Position the title image.
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50 # topCoord tracks where to position the top of the text
    titleRect.top = topCoord
    titleRect.centerx = int(win_wid / 2)
    topCoord += titleRect.height

    # Unfortunately, Pygame's font & text system only shows one line at
    # a time, so we can't use strings with \n newline characters in them.
    # So we will use a list with each line in it.
    instructionText = ['Press arrow keys to move.',
                       'Move forward to a enemy in order to kill.',
                       'R key to reset level, Esc to quit.',
                       'Kill 30 ememy to win.']

    # Start with drawing a blank color to the entire window:
    DISPLAYSURF.fill(BGCOLOR)

    # Draw the title image to the window:
    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)

    # Position and draw the text.
    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10 # 10 pixels will go in between each line of text.
        instRect.top = topCoord
        instRect.centerx = int(win_wid / 2)
        topCoord += instRect.height # Adjust for the height of the line.
        DISPLAYSURF.blit(instSurf, instRect)

    while True: # Main loop for the start screen.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return # user has pressed a key, so return.

        # Display the DISPLAYSURF contents to the actual screen.
        pygame.display.update()
        FPSCLOCK.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    # Each level must end with a blank line
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = [] # Will contain a list of level objects.
    levelNum = 0
    mapTextLines = [] # contains the lines for a single level's map.
    mapObj = [] # the map object made from the data in mapTextLines
    for lineNum in range(len(content)):
        # Process each line that was in the level file.
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            # Ignore the ; lines, they're comments in the level file.
            line = line[:line.find(';')]

        if line != '':
            # This line is part of the map.
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            # A blank line indicates the end of a level's map in the file.
            # Convert the text in mapTextLines into a level object.

            # Find the longest row in the map.
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            # Add spaces to the ends of the shorter rows. This
            # ensures the map will be rectangular.
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            # Convert mapTextLines to a map object.
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            # Loop through the spaces in the map and find the @, ., and $
            # characters for the starting game state.
            startx = None # The x and y for the player's starting position
            starty = None
            goals = [] # list of (x, y) tuples for each goal.
            barriers = [] # list of (x, y) for each barrier's starting position.
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        # '@' is player, '+' is player & goal
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        # '.' is goal, '*' is barrier & goal
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        # '$' is barrier
                        barriers.append((x, y))


            # Create level object and starting game state object.
            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'barriers': barriers}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            # Reset the variables for reading the next map.
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            SolList = []
            # gameStateObj['solier'] = []
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    '''Changes any values matching oldCharacter on the map object to
    newCharacter at the (x, y) position, and does the same for the
    positions to the left, right, down, and up of (x, y), recursively.'''

    # In this game, the flood fill algorithm creates the inside/outside
    # floor distinction. This is a "recursive" function.
    # For more info on the Flood Fill algorithm, see:
    #   http://en.wikipedia.org/wiki/Flood_fill
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter) # call right
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter) # call left
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter) # call down
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter) # call up


def drawMap(mapObj, gameStateObj, goals):
    """Draws the map to a Surface object, including the player and
    barriers. This function does not call pygame.display.update(), nor
    does it draw the "Level" and "Steps" text in the corner."""

    # mapSurf will be the single Surface object that the tiles are drawn
    # on, so that it is easy to position the entire map on the DISPLAYSURF
    # Surface object. First, the width and height must be calculated.
    mapSurfWidth = len(mapObj) * blo_wid
    mapSurfHeight = (len(mapObj[0]) - 1) * blo_hei_floor + blo_hei
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR) # start with a blank color on the surface.

    # Draw the tile sprites onto this surface.
    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * blo_wid, y * blo_hei_floor, blo_wid, blo_hei))
            spaceRectD = pygame.Rect((x * blo_wid+10, y * blo_hei_floor+10, blo_wid, blo_hei))
            spaceRectY = pygame.Rect((x * blo_wid-50, y * blo_hei_floor-10, blo_wid, blo_hei))
            turnRect = pygame.Rect((1,1,1,1))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDEDECOMAPPING:
                baseTile = TILEMAPPING[' ']

            # First draw the base ground/wall tile.
            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in OUTSIDEDECOMAPPING:
                # Draw any tree/rock decorations that are on this tile.
                mapSurf.blit(OUTSIDEDECOMAPPING[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['barriers']:
                if (x, y) in goals:
                    # A goal AND barrier are on this space, draw goal first.
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)
                # Then draw the barrier sprite.
                mapSurf.blit(IMAGESDICT['barrier'], spaceRect)
            elif (x, y) in goals:
                # Draw a goal without a barrier on it.
                mapSurf.blit(IMAGESDICT['uncovered goal'], spaceRect)

            # Last draw the player on the board.
            if (x, y) == gameStateObj['player']:
                # Note: The value "currentImage" refers
                # to a key in "PLAYERIMAGES" which has the
                # specific player image we want to show.
                global getDamage, LeftSide, isAttacking, hitenemy, hitplayer
                if getDamage:
                    if LeftSide:
                        mapSurf.blit(PLAYERIMAGES[5], spaceRectD)
                        getDamage = False
                    else:
                        mapSurf.blit(PLAYERIMAGES[4], spaceRectD)
                        getDamage = False
                    #hitplayer.play()
                elif isAttacking:
                    if LeftSide:
                        mapSurf.blit(PLAYERIMAGES[3], spaceRect)
                        mapSurf.blit(PLAYERIMAGES[-1], spaceRectY)
                        isAttacking = False
                    else:
                        mapSurf.blit(PLAYERIMAGES[2], spaceRect)
                        mapSurf.blit(PLAYERIMAGES[-1], spaceRectY)
                        isAttacking = False
                    #hitenemy.play()
                else:
                    if LeftSide:
                        mapSurf.blit(PLAYERIMAGES[1], spaceRect)
                    else:
                        mapSurf.blit(PLAYERIMAGES[0], spaceRect)
                    time.sleep(0.03)

            if 'soldier' in gameStateObj:
                if (x, y) in gameStateObj['soldier']:
                    mapSurf.blit(PLAYERIMAGES[6], spaceRect)

    # global YourTurn
    '''if YourTurn == True:
        mapSurf.blit(IMAGESDICT['yourturn'], turnRect)
    else:
        mapSurf.blit(IMAGESDICT['enemyturn'],turnRect)
        time.sleep(1)'''

        # mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
        # mapSurf.blit=pygame.transform.flip(PLAYERIMAGES, False, False)

    return mapSurf


def isLevelFinished():
    """Returns True if all the goals have barriers in them."""
    global score
    if score >=30:
        return True
    else:
        return False


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
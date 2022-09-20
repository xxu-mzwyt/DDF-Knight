import random
import sys
import copy
import os
import pygame
import time
from pygame.locals import *

# 初始化
FPS = 30
# 窗口与方块尺寸
win_wid = 1366
win_hei = 768
blo_wid = 50
blo_hei = 85
blo_hei_floor = 40

cam_spe = 5
global isAttacking
BGCOLOR = (0, 0, 0)
TEXTCOLOR = (255, 255, 255)
getDamage = False
LeftSide = False
isAttacking = False
pygame.mixer.init()
hitplayer = pygame.mixer.Sound('hitplayer.ogg')
hitenemy = pygame.mixer.Sound('hitenemy.ogg')
spawnenemy = pygame.mixer.Sound('spawnenemy.ogg')


def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES
    global currentImage, getDamage

    # Pygame initialization and basic set up of the global variables.
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.mixer.init()
    backsound = pygame.mixer.Sound('backsound.ogg')
    backsound.play(-1)
    # Because the Surface object stored in DISPLAYSURF was returned
    # from the pygame.display.set_mode() function, this is the
    # Surface object that is drawn to the actual computer screen
    # when pygame.display.update() is called.
    DISPLAYSURF = pygame.display.set_mode((win_wid,  win_hei), FULLSCREEN)

    pygame.display.set_caption('DDF_Knight')
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
                  'knight': pygame.image.load('knight.png'),
                  'knightL': pygame.image.load('knightL.png'),
                  'knight_attack': pygame.image.load('knight_attack.png'),
                  'knight_attackL': pygame.image.load('knight_attackL.png'),
                  'knight_hurted': pygame.image.load('knight_hurted.png'),
                  'knight_hurtedL': pygame.image.load('knight_hurtedL.png'),
                  'lord': pygame.image.load('lord.png'),
                  'shieldman': pygame.image.load('shieldman.png'),
                  'soldier': pygame.image.load('soldier.png'),
                  'soldierL': pygame.image.load('soldierL.png'),
                  'soldier_attack': pygame.image.load('soldier_attack.png'),
                  'soldier_attackL': pygame.image.load('soldier_attackL.png'),
                  'soldier_die': pygame.image.load('soldier_die.png'),
                  'soldier_dieL': pygame.image.load('soldier_dieL.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png'),
                  'died': pygame.image.load('died.png'),
                  'solved': pygame.image.load('star_solved.png')}

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
                    IMAGESDICT['soldier_dieL']]

    start_screen()  # show the title screen until the user presses a key

    # Read in the levels from the text file. See the read_levelfile() for
    # details on the format of this file and how to make your own levels.
    levels = read_levelfile('DDFlevel.txt')
    current_level_index = 0

    # The main game loop. This loop runs a single level, when the user
    # finishes that level, the next/previous level is loaded.
    while 'soldier' != 'solier':  # main game loop
        # Run the level to actually start playing the game:
        result = run_level(levels, current_level_index)

        if result in ('solved', 'next'):
            # Go to the next level.
            current_level_index += 1
            if current_level_index >= len(levels):
                # If there are no more levels, go back to the first one.
                current_level_index = 0
        elif result == 'reset':
            pass  # Do nothing. Loop re-calls run_level() to reset the level


def run_level(levels, level_num):
    global currentImage, getDamage, YourTurn, soldier_list, health, MAXHEALTH, score, LeftSide, getDamage, keyPressed
    soldier_list = []
    level_obj = levels[level_num]
    map_obj = decorate_map(level_obj['map_obj'], level_obj['startState']['player'])
    gamestate_obj = copy.deepcopy(level_obj['startState'])
    map_needs_redraw = True  # set to True to call draw_map()

    map_width = len(map_obj) * blo_wid
    map_height = (len(map_obj[0]) - 1) * blo_hei_floor + blo_hei
    max_cam_xpan = abs(int(win_hei / 2) - int(map_height / 2)) + blo_wid
    max_cam_ypan = abs(int(win_wid / 2) - int(map_width / 2)) + blo_hei

    YourTurn = True
    getDamage = False
    level_complete = False
    # Track how much the camera has moved:
    camera_x = 0
    camera_y = 0
    # Track if the keys to move the camera are being held down:
    camera_up = False
    camera_down = False
    camera_left = False
    camera_right = False
    health = 5
    MAXHEALTH = 5
    score = 0
    while 'soldier' != 'solier':  # main game loop (while True)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
            if event.type == QUIT:
                # Player clicked the "X" at the corner of the window.
                terminate()
        #  Reset these variables:

        player_moveto = None
        keyPressed = False

        if health > 0:
            plrx = gamestate_obj['player'][0]
            plry = gamestate_obj['player'][1]
            if (plrx - 1, plry, 1) in soldier_list or (plrx - 1, plry, 2) in soldier_list\
            or (plrx - 2, plry, 1) in soldier_list or (plrx - 2, plry, 2) in soldier_list:
                player_moveto = 'left'
            elif (plrx + 1, plry, 1) in soldier_list or (plrx + 1, plry, 2) in soldier_list\
            or (plrx + 2, plry, 1) in soldier_list or (plrx + 2, plry, 2) in soldier_list:
                player_moveto = 'right'
            elif (plrx, plry - 1, 1) in soldier_list or (plrx, plry - 1, 2) in soldier_list\
            or (plrx, plry - 2, 1) in soldier_list or (plrx, plry - 2, 2) in soldier_list:
                player_moveto = 'up'
            elif (plrx, plry + 1, 1) in soldier_list or (plrx, plry + 1, 2) in soldier_list\
            or (plrx, plry + 2, 1) in soldier_list or (plrx, plry + 2, 2) in soldier_list:
                player_moveto = 'down'
            else:
                ran = random.randint(1,5)
                if ran == 1:
                    player_moveto = 'left'
                if ran == 2:
                    player_moveto = 'right'
                if ran == 3:
                    player_moveto = 'up'
                if ran == 4:
                    player_moveto = 'down'
        if health <= 0:
            time.sleep(2)
            filename = 'Score_Saves.txt'
            with open(filename, 'a') as f:
                f.write(str(score)+'\n')
            return 'reset'


        if player_moveto is not None and not level_complete:

            moved = make_move(map_obj, gamestate_obj, player_moveto)

            if moved:
                # increment the step counter.
                YourTurn = False
                for soldier in range(len(soldier_list)):
                    dire = random.randint(1, 5)
                    if dire == 1 and not is_wall(map_obj, soldier_list[soldier][0] - 1, soldier_list[soldier][1])\
                            and not (soldier_list[soldier][0] - 1, soldier_list[soldier][1], 1) in soldier_list \
                            and not (soldier_list[soldier][0] - 1, soldier_list[soldier][1], 2) in soldier_list \
                            and not (soldier_list[soldier][0] - 1, soldier_list[soldier][1]) == gamestate_obj['player']:
                        soldier_list[soldier] = (soldier_list[soldier][0] - 1, soldier_list[soldier][1], 1)
                    if dire == 2 and not is_wall(map_obj, soldier_list[soldier][0] + 1, soldier_list[soldier][1])\
                            and not (soldier_list[soldier][0] + 1, soldier_list[soldier][1], 1) in soldier_list \
                            and not (soldier_list[soldier][0] + 1, soldier_list[soldier][1], 2) in soldier_list \
                            and not (soldier_list[soldier][0] + 1, soldier_list[soldier][1]) == gamestate_obj['player']:
                        soldier_list[soldier] = (soldier_list[soldier][0] + 1, soldier_list[soldier][1], 2)
                    if dire == 3 and not is_wall(map_obj, soldier_list[soldier][0], soldier_list[soldier][1] - 1)\
                            and not (soldier_list[soldier][0], soldier_list[soldier][1] - 1, 1) in soldier_list \
                            and not (soldier_list[soldier][0], soldier_list[soldier][1] - 1, 2) in soldier_list \
                            and not (soldier_list[soldier][0], soldier_list[soldier][1] - 1) == gamestate_obj['player']:
                        soldier_list[soldier] = (soldier_list[soldier][0], soldier_list[soldier][1] - 1, soldier_list[soldier][2])
                    if dire == 4 and not is_wall(map_obj, soldier_list[soldier][0], soldier_list[soldier][1] + 1)\
                            and not (soldier_list[soldier][0], soldier_list[soldier][1] + 1, 1) in soldier_list \
                            and not (soldier_list[soldier][0], soldier_list[soldier][1] + 1, 2) in soldier_list \
                            and not (soldier_list[soldier][0], soldier_list[soldier][1] + 1) == gamestate_obj['player']:
                        soldier_list[soldier] = (soldier_list[soldier][0], soldier_list[soldier][1] + 1, soldier_list[soldier][2])
                for soldier in range(len(soldier_list)):
                    if gamestate_obj['player'][0] == soldier_list[soldier][0] - 1\
                            and gamestate_obj['player'][1] == soldier_list[soldier][1]:
                        health -= 1
                        getDamage = True
                        
                    if gamestate_obj['player'][0] == soldier_list[soldier][0] + 1\
                            and gamestate_obj['player'][1] == soldier_list[soldier][1]:
                        health -= 1
                        getDamage = True
                    if gamestate_obj['player'][0] == soldier_list[soldier][0]\
                            and gamestate_obj['player'][1] == soldier_list[soldier][1] - 1:
                        health -= 1
                        getDamage = True
                    if gamestate_obj['player'][0] == soldier_list[soldier][0]\
                            and gamestate_obj['player'][1] == soldier_list[soldier][1] + 1:
                        health -= 1
                        getDamage = True

                if len(soldier_list) <= 10:

                    if random.randint(1, 15) == 1 and not (1, 1) in soldier_list:
                        soldier_list.append((1, 1, 1))
                        spawnenemy.play()
                    if random.randint(1, 15) == 1 and not (25, 1) in soldier_list:
                        soldier_list.append((25, 1, 2))
                        spawnenemy.play()
                    if random.randint(1, 15) == 1 and not (1, 15) in soldier_list:
                        soldier_list.append((1, 17, 1))
                        spawnenemy.play()
                    if random.randint(1, 15) == 1 and not (24, 15) in soldier_list:
                        soldier_list.append((24, 17, 2))
                        spawnenemy.play()

                gamestate_obj['soldier'] = soldier_list

                YourTurn = True
            if level_finished():
                # level is solved, we should show the "Solved!" image.
                level_complete = True
                keyPressed = False

        DISPLAYSURF.fill(BGCOLOR)

        if map_needs_redraw:
            map_surf = draw_map(map_obj, gamestate_obj, level_obj['goals'])

        if camera_up and camera_y < max_cam_xpan:
            camera_y += cam_spe
        elif camera_down and camera_y > -max_cam_xpan:
            camera_y -= cam_spe
        if camera_left and camera_x < max_cam_ypan:
            camera_x += cam_spe
        elif camera_right and camera_x > -max_cam_ypan:
            camera_x -= cam_spe

        map_surf_rect = map_surf.get_rect()
        map_surf_rect.center = (int(win_wid / 2) + camera_x, int(win_hei / 2) + camera_y)

        # Draw map_surf to the DISPLAYSURF Surface object.
        DISPLAYSURF.blit(map_surf, map_surf_rect)
        draw_health(health)
        font = pygame.font.SysFont("calibri", 40)
        score2 = font.render(str(score), True, (100, 100, 255))
        DISPLAYSURF.blit(score2, (1300., 10.))

        if level_complete:
            # is solved, show the "Solved!" image until the player
            # has pressed a key.
            solve_rect = IMAGESDICT['solved'].get_rect()
            solve_rect.center = (int(win_wid / 2), int(win_hei / 2))
            DISPLAYSURF.blit(IMAGESDICT['solved'], solve_rect)
            if keyPressed:
                return 'solved'

        pygame.display.update()  # draw DISPLAYSURF to the screen.
        FPSCLOCK.tick()


def draw_health(current_health):
    global keyPressed
    for i in range(current_health):  # draw red health bars
        pygame.draw.rect(DISPLAYSURF, (255, 0, 0),   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH):  # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, (0, 0, 0), (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)
    if current_health <= 0:
        # is solved, show the "Solved!" image until the player
        # has pressed a key.
        solve_rect = IMAGESDICT['died'].get_rect()
        solve_rect.center = (int(win_wid / 2), int(win_hei / 2))
        DISPLAYSURF.blit(IMAGESDICT['died'], solve_rect)
        if keyPressed:
            return 'reset'


def is_wall(map_obj, x, y):
    """Returns True if the (x, y) position on
    the map is a wall, otherwise return False."""
    if x < 0 or x >= len(map_obj) or y < 0 or y >= len(map_obj[x]):
        return False  # x and y aren't actually on the map.
    elif map_obj[x][y] in ('#', 'x', '*'):
        return True  # wall is blocking
    return False


def decorate_map(map_obj, startxy):
    """Makes a copy of the given map object and modifies it.
    Here is what is done to it:
        * Walls that are corners are turned into corner pieces.
        * The outside/inside floor tile distinction is made.
        * Tree/rock decorations are randomly added to the outside tiles.

    Returns the decorated map object."""

    startx, starty = startxy  # Syntactic sugar

    # Copy the map object so we don't modify the original passed
    map_obj_opy = copy.deepcopy(map_obj)

    # Remove the non-wall characters from the map data
    for x in range(len(map_obj_opy)):
        for y in range(len(map_obj_opy[0])):
            if map_obj_opy[x][y] in ('$', '.', '@', '+', '*'):
                map_obj_opy[x][y] = ' '

    # Flood fill to determine inside/outside floor tiles.
    flood_fill(map_obj_opy, startx, starty, ' ', 'o')

    # Convert the adjoined walls into corner tiles.
    for x in range(len(map_obj_opy)):
        for y in range(len(map_obj_opy[0])):

            if map_obj_opy[x][y] == '#':
                if (is_wall(map_obj_opy, x, y-1) and is_wall(map_obj_opy, x+1, y)) or \
                   (is_wall(map_obj_opy, x+1, y) and is_wall(map_obj_opy, x, y+1)) or \
                   (is_wall(map_obj_opy, x, y+1) and is_wall(map_obj_opy, x-1, y)) or \
                   (is_wall(map_obj_opy, x-1, y) and is_wall(map_obj_opy, x, y-1)):
                    map_obj_opy[x][y] = 'x'

            elif map_obj_opy[x][y] == ' ' and random.randint(0, 99) < 20:
                map_obj_opy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return map_obj_opy


def is_blocked(map_obj, gamestate_obj, x, y):
    """Returns True if the (x, y) position on the map is
    blocked by a wall or barrier, otherwise return False."""

    if is_wall(map_obj, x, y):
        return True

    elif x < 0 or x >= len(map_obj) or y < 0 or y >= len(map_obj[x]):
        return True  # x and y aren't actually on the map.

    elif (x, y) in gamestate_obj['barriers']:
        return True  # a barrier is blocking

    return False


def make_move(map_obj, gamestate_obj, player_moveto):
    global score, isAttacking
    """Given a map and game state object, see if it is possible for the
    player to make the given move. If it is, then change the player's
    position (and the position of any pushed barrier). If not, do nothing.

    Returns True if the player moved, otherwise False."""

    # Make sure the player can move in the direction they want.
    playerx, playery = gamestate_obj['player']

    # This variable is "syntactic sugar". Typing "barriers" is more
    # readable than typing "gamestate_obj['barriers']" in our code.
    barriers = gamestate_obj['barriers']

    # The code for handling each of the directions is so similar aside
    # from adding or subtracting 1 to the x/y coordinates. We can
    # simplify it by using the x_set and y_set variables.
    if player_moveto == 'up':
        x_set = 0
        y_set = -1
        if (gamestate_obj['player'][0], gamestate_obj['player'][1] - 2, 1) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0], gamestate_obj['player'][1] - 2, 1))
            score += 1
            isAttacking = 2
        elif (gamestate_obj['player'][0], gamestate_obj['player'][1] - 2, 2) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0], gamestate_obj['player'][1] - 2, 2))
            isAttacking = 2
            score += 1
        if (gamestate_obj['player'][0], gamestate_obj['player'][1] - 1, 1) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0], gamestate_obj['player'][1] - 1, 1))
            score += 1
            isAttacking = 2
        elif (gamestate_obj['player'][0], gamestate_obj['player'][1] - 1, 2) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0], gamestate_obj['player'][1] - 1, 2))
            isAttacking = 2
            score += 1
    elif player_moveto == 'right':
        x_set = 1
        y_set = 0
        if (gamestate_obj['player'][0] + 2, gamestate_obj['player'][1], 1) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0] + 2, gamestate_obj['player'][1], 1))
            score += 1
            isAttacking = 2
        elif (gamestate_obj['player'][0] + 2, gamestate_obj['player'][1], 2) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0] + 2, gamestate_obj['player'][1], 2))
            score += 1
            isAttacking = 2
        if (gamestate_obj['player'][0] + 1, gamestate_obj['player'][1], 1) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0] + 1, gamestate_obj['player'][1], 1))
            score += 1
            isAttacking = 2
        elif (gamestate_obj['player'][0] + 1, gamestate_obj['player'][1], 2) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0] + 1, gamestate_obj['player'][1], 2))
            score += 1
            isAttacking = 2
    elif player_moveto == 'down':
        x_set = 0
        y_set = 1
        if (gamestate_obj['player'][0], gamestate_obj['player'][1] + 2, 1) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0], gamestate_obj['player'][1] + 2, 1))
            score += 1
            isAttacking = 2
        elif (gamestate_obj['player'][0], gamestate_obj['player'][1] + 2, 2) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0], gamestate_obj['player'][1] + 2, 2))
            score += 1
            isAttacking = 2
        if (gamestate_obj['player'][0], gamestate_obj['player'][1] + 1, 1) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0], gamestate_obj['player'][1] + 1, 1))
            score += 1
            isAttacking = 2
        elif (gamestate_obj['player'][0], gamestate_obj['player'][1] + 1, 2) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0], gamestate_obj['player'][1] + 1, 2))
            score += 1
            isAttacking = 2
    elif player_moveto == 'left':
        x_set = -1
        y_set = 0
        if (gamestate_obj['player'][0] - 2, gamestate_obj['player'][1], 1) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0] - 2, gamestate_obj['player'][1], 1))
            score += 1
            isAttacking = 2
        elif (gamestate_obj['player'][0] - 2, gamestate_obj['player'][1], 2) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0] - 2, gamestate_obj['player'][1], 2))
            score += 1
            isAttacking = 2
        if (gamestate_obj['player'][0] - 1, gamestate_obj['player'][1], 1) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0] - 1, gamestate_obj['player'][1], 1))
            score += 1
            isAttacking = 2
        elif (gamestate_obj['player'][0] - 1, gamestate_obj['player'][1], 2) in soldier_list:
            soldier_list.remove((gamestate_obj['player'][0] - 1, gamestate_obj['player'][1], 2))
            score += 1
            isAttacking = 2
        # pygame.transform.flip(map_surf, xbool, ybool)
        # See if the player can move in that direction.

        # bookmark:playermove

    if is_wall(map_obj, playerx + x_set, playery + y_set):
        return False
    else:
        if (playerx + x_set, playery + y_set) in barriers:
            return False
        # Move the player upwards.
        gamestate_obj['player'] = (playerx + x_set, playery + y_set)
        return True


def start_screen():
    """Display the start screen (which has the title and instructions)
    until the player presses a key. Returns None."""

    # Position the title image.
    title_rect = IMAGESDICT['title'].get_rect()
    top_coord = 50  # top_coord tracks where to position the top of the text
    title_rect.top = top_coord
    title_rect.centerx = int(win_wid / 2)
    top_coord += title_rect.height

    # Unfortunately, Pygame's font & text system only shows one line at
    # a time, so we can't use strings with \n newline characters in them.
    # So we will use a list with each line in it.
    instruction_text = ['Press WASD keys to move, arrow keys to move camera.',
                        'Move forward to a enemy in order to kill.',
                        'R key to reset level, Esc to quit.',
                        'Kill 30 ememy to win.']

    # Start with drawing a blank color to the entire window:
    DISPLAYSURF.fill(BGCOLOR)

    # Draw the title image to the window:
    DISPLAYSURF.blit(IMAGESDICT['title'], title_rect)

    # Position and draw the text.
    for i in range(len(instruction_text)):
        inst_surf = BASICFONT.render(instruction_text[i], 1, TEXTCOLOR)
        inst_rect = inst_surf.get_rect()
        top_coord += 10  # 10 pixels will go in between each line of text.
        inst_rect.top = top_coord
        inst_rect.centerx = int(win_wid / 2)
        top_coord += inst_rect.height  # Adjust for the height of the line.
        DISPLAYSURF.blit(inst_surf, inst_rect)

    while 'soldier' != 'solier':  # Main loop for the start screen.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return  # user has pressed a key, so return.

        # Display the DISPLAYSURF contents to the actual screen.
        pygame.display.update()
        FPSCLOCK.tick()


def read_levelfile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % filename
    map_file = open(filename, 'r')
    # Each level must end with a blank line
    content = map_file.readlines() + ['\r\n']
    map_file.close()

    levels = []  # Will contain a list of level objects.
    level_num = 0
    map_text_lines = []  # contains the lines for a single level's map.
    map_obj = []  # the map object made from the data in map_text_lines
    for lineNum in range(len(content)):
        # Process each line that was in the level file.
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            # Ignore the ; lines, they're comments in the level file.
            line = line[:line.find(';')]

        if line != '':
            # This line is part of the map.
            map_text_lines.append(line)
        elif line == '' and len(map_text_lines) > 0:
            # A blank line indicates the end of a level's map in the file.
            # Convert the text in map_text_lines into a level object.

            # Find the longest row in the map.
            max_width = -1
            for i in range(len(map_text_lines)):
                if len(map_text_lines[i]) > max_width:
                    max_width = len(map_text_lines[i])
            # Add spaces to the ends of the shorter rows. This
            # ensures the map will be rectangular.
            for i in range(len(map_text_lines)):
                map_text_lines[i] += ' ' * (max_width - len(map_text_lines[i]))

            # Convert map_text_lines to a map object.
            for x in range(len(map_text_lines[0])):
                map_obj.append([])
            for y in range(len(map_text_lines)):
                for x in range(max_width):
                    map_obj[x].append(map_text_lines[y][x])

            # Loop through the spaces in the map and find the @, ., and $
            # characters for the starting game state.
            startx = None  # The x and y for the player's starting position
            starty = None
            goals = []  # list of (x, y) tuples for each goal.
            barriers = []  # list of (x, y) for each barrier's starting position.
            for x in range(max_width):
                for y in range(len(map_obj[x])):
                    if map_obj[x][y] in ('@', '+'):
                        # '@' is player, '+' is player & goal
                        startx = x
                        starty = y
                    if map_obj[x][y] in ('.', '+', '*'):
                        # '.' is goal, '*' is barrier & goal
                        goals.append((x, y))
                    if map_obj[x][y] in ('$', '*'):
                        # '$' is barrier
                        barriers.append((x, y))

            # Create level object and starting game state object.
            gamestate_obj = {'player': (startx, starty),
                             'stepCounter': 0,
                             'barriers': barriers}
            level_obj = {'width': max_width,
                         'height': len(map_obj),
                         'map_obj': map_obj,
                         'goals': goals,
                         'startState': gamestate_obj}

            levels.append(level_obj)

            # Reset the variables for reading the next map.
            map_text_lines = []
            map_obj = []
            level_num += 1
    return levels


def flood_fill(map_obj, x, y, old_character, new_character):
    # Changes any values matching old_character on the map object to
    # new_character at the (x, y) position, and does the same for the
    # positions to the left, right, down, and up of (x, y), recursively.
    # In this game, the flood fill algorithm creates the inside/outside
    # floor distinction. This is a "recursive" function.
    # For more info on the Flood Fill algorithm, see:
    #   http://en.wikipedia.org/wiki/Flood_fill
    if map_obj[x][y] == old_character:
        map_obj[x][y] = new_character

    if x < len(map_obj) - 1 and map_obj[x+1][y] == old_character:
        flood_fill(map_obj, x+1, y, old_character, new_character)  # call right
    if x > 0 and map_obj[x-1][y] == old_character:
        flood_fill(map_obj, x-1, y, old_character, new_character)  # call left
    if y < len(map_obj[x]) - 1 and map_obj[x][y+1] == old_character:
        flood_fill(map_obj, x, y+1, old_character, new_character)  # call down
    if y > 0 and map_obj[x][y-1] == old_character:
        flood_fill(map_obj, x, y-1, old_character, new_character)  # call up


def draw_map(map_obj, gamestate_obj, goals):
    """Draws the map to a Surface object, including the player and
    barriers. This function does not call pygame.display.update(), nor
    does it draw the "Level" and "Steps" text in the corner."""

    # map_surf will be the single Surface object that the tiles are drawn
    # on, so that it is easy to position the entire map on the DISPLAYSURF
    # Surface object. First, the width and height must be calculated.
    map_surfwidth = len(map_obj) * blo_wid
    map_surfheight = (len(map_obj[0]) - 1) * blo_hei_floor + blo_hei
    map_surf = pygame.Surface((map_surfwidth, map_surfheight))
    map_surf.fill(BGCOLOR)  # start with a blank color on the surface.

    # Draw the tile sprites onto this surface.
    for x in range(len(map_obj)):
        for y in range(len(map_obj[x])):
            space_rect = pygame.Rect((x * blo_wid, y * blo_hei_floor, blo_wid, blo_hei))
            space_rect_damage = pygame.Rect((x * blo_wid+10, y * blo_hei_floor+10, blo_wid, blo_hei))
            if map_obj[x][y] in TILEMAPPING:
                base_tile = TILEMAPPING[map_obj[x][y]]
            elif map_obj[x][y] in OUTSIDEDECOMAPPING:
                base_tile = TILEMAPPING[' ']

            # First draw the base ground/wall tile.
            map_surf.blit(base_tile, space_rect)

            if map_obj[x][y] in OUTSIDEDECOMAPPING:
                # Draw any tree/rock decorations that are on this tile.
                map_surf.blit(OUTSIDEDECOMAPPING[map_obj[x][y]], space_rect)

            elif (x, y) in goals:
                # Draw a enemy spwan point.
                map_surf.blit(IMAGESDICT['uncovered goal'], space_rect)

            # Last draw the player on the board.
            if (x, y) == gamestate_obj['player']:
                # Note: The value getDamege, isAttacking and LeftSide refers
                # to a key in "PLAYERIMAGES" which has the
                # specific player image we want to show.
                global getDamage, LeftSide, isAttacking, hitenemy, hitplayer
                if getDamage:
                    if LeftSide:
                        map_surf.blit(PLAYERIMAGES[5], space_rect_damage)
                        getDamage = False
                    else:
                        map_surf.blit(PLAYERIMAGES[4], space_rect_damage)
                        getDamage = False
                    hitplayer.play()
                elif isAttacking > 0:
                    if isAttacking == 2:
                        hitenemy.play()
                    if LeftSide:
                        map_surf.blit(PLAYERIMAGES[3], space_rect)
                        isAttacking -= 1
                    else:
                        map_surf.blit(PLAYERIMAGES[2], space_rect)
                        isAttacking -= 1

                else:
                    if LeftSide:
                        map_surf.blit(PLAYERIMAGES[1], space_rect)
                    else:
                        map_surf.blit(PLAYERIMAGES[0], space_rect)
            # Draw enemys.
            if 'soldier' in gamestate_obj:
                if (x, y, 1) in gamestate_obj['soldier']:
                    map_surf.blit(PLAYERIMAGES[7], space_rect)
                if (x, y, 2) in gamestate_obj['soldier']:
                    map_surf.blit(PLAYERIMAGES[6], space_rect)
            # Draw barriers last in order to covers enemys.
            if (x, y) in gamestate_obj['barriers']:
                map_surf.blit(IMAGESDICT['barrier'], space_rect)

    return map_surf


def level_finished():
    # Returns True if you kill 30 enemys.
    global score
    if score >= 30:
        return True
    else:
        return False


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

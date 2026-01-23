# source: https://www.hackster.io/synd/conway-s-game-of-life-on-micropython-feb78a
import machine
import neopixel
import utime
import urandom
import array

PIXEL_WIDTH = 8
PIXEL_HEIGHT = 8
MAX_BRIGHT = 20
_NeoPixel = 23 # définition du port NeoPixel (GP23)


board = [[0 for j in range(PIXEL_WIDTH + 1)]for i in range(PIXEL_HEIGHT + 1)]
pixels = neopixel.NeoPixel(machine.Pin(_NeoPixel), PIXEL_WIDTH*PIXEL_HEIGHT)

def conway_step():
    changed = False
    for x in range (PIXEL_HEIGHT):
        for y in range (PIXEL_WIDTH):
            num_neighbours = board[x-1][y-1] + board[x][y-1] + board[x+1][y-1] + board[x-1][y]
            num_neighbours = num_neighbours + board[x+1][y] + board[x-1][y+1] + board[x][y+1] + board[x+1][y+1]
            self = board[x][y]
            if self and not (2 <= num_neighbours <= 3):
                if board[x][y]:
                    board[x][y] = 0
                    changed = True
            elif not self and num_neighbours == 3:
                if not board[x][y]:
                    board[x][y] = 1
                    changed = True
    return changed

def conway_rand():
    print("Generate New Life!")
    for x in range (PIXEL_HEIGHT):
        for y in range (PIXEL_WIDTH):
            board[x][y] = urandom.randint(0, 1)

pixels.fill((0,0,0))
pixels.write()

refresh_needed = True
color = (10, 10, 10)

while True:
    if (refresh_needed):
        conway_rand()
        color = (urandom.randint(0,MAX_BRIGHT), urandom.randint(0,MAX_BRIGHT), urandom.randint(0,MAX_BRIGHT))
        refresh_needed = False

    if not conway_step():
        refresh_needed = True
#    print("---------------------------")
    for x in range (PIXEL_HEIGHT):
#        print(board[x])
        for y in range (PIXEL_WIDTH):
            if board[x][y]:
                pixels[x * 8 + y] = color
            else:
                pixels[x * 8 + y] = (0, 0, 0)
#    print("---------------------------")
    pixels.write()
    utime.sleep(0.1)
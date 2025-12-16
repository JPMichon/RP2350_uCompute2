from machine import I2C, UART, SPI, PWM, Pin
import st7789 as st7789
import time
import framebuf2
import utime
import random

#Configuration des Ports pour le uCompute V1.x
_MicroSD_Detect = 7 # détection de la présence d'une carte MicroSD (GP7)
_MicroSD_Select = 13 # définition de la pin Select du SDCARD (GP13)
_W5500_Select = 8 # définition de la pin Select du W5500 (GP8)
_W5500_Reset = 10 # définition de la pin Reset du W5500 (GP10)
_SPI1_SCK = 14 # SPI1_shared Clock
_SPI1_MOSI = 15 # SPI1_shared MOSI
_SPI1_MISO = 12 # SPI1_shared MISO
_ST7789_SCK = 2 # définition de la pin Clock du ST7789 (GP2) SPI0
_ST7789_MOSI = 3 # définition de la pin MOSI du ST7789 (GP3) SPI0
_ST7789_RESET = 4 # définition de la pin Reset du ST7789 (GP4)
_ST7789_DC = 5 # définition de la pinSelect du ST7789 (GP5)
_ST7789_BL = 6 # définition de la pinBacklit du ST7789 (GP6)

_Led_System = 25 # définition du port  del systeme (GP25)
_I2C_SDA = 20 # définition de Data du I2C(0) (GP20)
_I2C_SCL = 21 # définition de SCL du I2C(0) (GP21)
_Buzzer = 11 # définition du  buzzer (GP11)
_NeoPixel = 23 # définition du port NeoPixel (GP23)
_NeoPixel_nbr = 8 # nombre de neopixel sur le port
_EEPROM_ADDR = 0x50 # adresse du eeprom
_Boutons = 26 # définition du port analogue des boutons (GP26)
_UART = 0 # UART par defaut
_TX_PIN = 0 # TX Pin (GP0)
_RX_PIN = 1 # TX Pin (GP1)
_BaudRate = 9600 # Baud rate du UART
# set landscape screen
screen_width = 240
screen_height = 240
screen_rotation = 1



#-------------------------------------
#
# # Début de l'initialisation 
#

#Initialisation des IOs
System_LED = Pin(_Led_System,Pin.OUT)
MicroSD_Detect = Pin(_MicroSD_Detect,Pin.IN)
BTN_Analogue = machine.ADC(_Boutons) #Diviseur de tension des boutons

spi = SPI(0,baudrate=60000000,polarity=1,phase=0,bits=8,firstbit=SPI.MSB,sck=Pin(_ST7789_SCK),mosi=Pin(_ST7789_MOSI))
display = st7789.ST7789(spi,screen_width,screen_height,reset=Pin(_ST7789_RESET, Pin.OUT),dc=Pin(_ST7789_DC, Pin.OUT),backlight=Pin(_ST7789_BL, Pin.OUT),rotation=screen_rotation)


# Initialisation du FrameBuffer
# FrameBuffer needs 2 bytes for every RGB565 pixel
buffer_width = 240
buffer_height = 240
buffer = bytearray(buffer_width * buffer_height * 2)
fbuf = framebuf2.FrameBuffer(buffer, buffer_width, buffer_height, framebuf2.RGB565)
fbuf.fill(st7789.WHITE)

#-------------------------------------
# John Conway's Game of Life for the Raspberry Pi Pico Game Boy
# based on https://github.com/YouMakeTech/Pi-Pico-Game-Boy/blob/main/GameOfLife.py
# 
#-------------------------------------
# Game parameters
WIDTH = screen_width       # screen width in pixels
HEIGHT = screen_height      # screen height in pixels
CELL_SIZE = 8            # width and height of cells in pixels
POPULATION_PERCENT = 12  # Initial population size as function of total surface in %
BACKGROUND_COLOR = st7789.BLACK
CELL_COLOR = st7789.WHITE

# Board initialisation
BOARD_SIZE_X = int(WIDTH/CELL_SIZE)
BOARD_SIZE_Y = int(HEIGHT/CELL_SIZE)
BOARD_SURFACE = BOARD_SIZE_X * BOARD_SIZE_Y

board=[]
for i in range(0,BOARD_SIZE_Y):
    line = []
    for j in range(0,BOARD_SIZE_X):
        line.append(0)
    board.append(line)
 
 # Initial number of cells 
NUMBER_OF_CELLS = int((POPULATION_PERCENT)/100 * BOARD_SURFACE);

# Create the initial population
for i in range(0,NUMBER_OF_CELLS):
    # Randomly place cells on the board
    board[random.randint(0,BOARD_SIZE_Y-1)][random.randint(0,BOARD_SIZE_X-1)] = CELL_COLOR
 
 # run the animation
while True:
    # Update the screen
    fbuf.fill(BACKGROUND_COLOR) # Efface l'écran (le framefuffer)
    for i in range(0,BOARD_SIZE_Y):
        for j in range(0,BOARD_SIZE_X):
            if board[i][j]!=0:
                fbuf.rect(j*CELL_SIZE,i*CELL_SIZE,CELL_SIZE,CELL_SIZE,board[i][j], True) #boite vide
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)
    
    # count number of neighbors for each position
    for i in range(0,BOARD_SIZE_Y):
        for j in range(0,BOARD_SIZE_X):
            number_neighbors = 0
            
            if i>1 and j>1 and board[i-1][j-1]!=0:
                number_neighbors+=1
            if i>1 and board[i-1][j]!=0:
                number_neighbors+=1
            if i>1 and j<BOARD_SIZE_X-1 and board[i-1][j+1]!=0:
                number_neighbors+=1
            if i<BOARD_SIZE_Y-1 and j>1 and board[i+1][j-1]!=0:
                number_neighbors+=1
            if i<BOARD_SIZE_Y-1 and board[i+1][j]!=0:
                number_neighbors+=1
            if i<BOARD_SIZE_Y-1 and j<BOARD_SIZE_Y-1 and board[i+1][j+1]!=0:
                number_neighbors+=1
            if j>1 and board[i][j-1]!=0:
                number_neighbors+=1
            if j<BOARD_SIZE_X-1 and board[i][j+1]!=0:
                number_neighbors+=1
            
            # The game's rules
            if board[i][j]!=BACKGROUND_COLOR:
                # There is a living cell at row #i col #j
                # It survives only if it surrounded by 2 or 3 neighbors
                if number_neighbors<2 or number_neighbors>3:
                    board[i][j] = 0
            else:
                # row #i col #j is empty
                # Create a new cell at (i,j) if it is surrounded by exactly 3 neighbors
                if number_neighbors==3:
                    board[i][j] = CELL_COLOR    
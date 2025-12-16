from machine import I2C, UART, SPI, PWM, Pin
from random import random, seed, randint
from utime import sleep_us, ticks_cpu, ticks_us, ticks_diff

import st7789 as st7789
import EEPROM_CAT24C128
import uos
import neopixel
import time
import sdcard
import utime
import rp2
import os
import sys
import gc
import framebuf2


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
Nombre_Menu=9 # le compte de menu commence a 0 maximum de 8 menu
#-------------------------------------
# Configuration des variables pour les leds neopixels (WS2812)
NeoPixel_nbr = 8 # nombre de neopixel sur le port
NeoPixel_brightness = 0.1

    
#-------------------------------------
#
# # Début de l'initialisation 
#

#Initialisation des IOs
System_LED = Pin(_Led_System,Pin.OUT)
MicroSD_Detect = Pin(_MicroSD_Detect,Pin.IN)
BTN_Analogue = machine.ADC(_Boutons) #Diviseur de tension des boutons

#Initialisation du UART
uart = UART(_UART, baudrate=_BaudRate, tx=Pin(_TX_PIN), rx=Pin(_RX_PIN))
#uart.init(_BaudRate, bits=8, parity=None, stop=1) # init with given parameters

#Initialisation du I2C
i2c=I2C(0,sda=Pin(_I2C_SDA), scl=Pin(_I2C_SCL), freq=200000)

# va chercher les stats de la memoire flash
stat = os.statvfs("/")
size = stat[1] * stat[2]
free = stat[0] * stat[3]
used = size - free


# Booting message envoyé sur le port serie
uart.write(b'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\r')
uart.write(b'------------------------\n\r')
uart.write(b'uCompute\n\r')
uart.write(str(os.uname().machine))
uart.write(b' @ ')
uart.write(str(int((machine.freq()/1000000))))
uart.write(b' Mhz\n\n\r')
uart.write(b'Environement\n\r')
uart.write(str(os.uname().version))
uart.write(b' \n\n\r')
utime.sleep(.5)
uart.write(b'Memory\n\r')
uart.write(b'  Heap Allocated: ')
uart.write(str(gc.mem_alloc()))
uart.write(b' bytes\n\r')
uart.write(b'  Heap Free: ')
uart.write(str(gc.mem_free()))
uart.write(b' bytes\n\n\r')
uart.write(b'Flash\n\r')
uart.write(b'  Size: ')
uart.write(str(int((size)/1024)))
uart.write(b' KB\n\r')
uart.write(b'  Used: ')
uart.write(str(int((size - free)/1024)))
uart.write(b' KB\n\r')
uart.write(b'  Free: ')
uart.write(str(int((free)/1024)))
uart.write(b' KB\n\n\r')
uart.write(b'------------------------\n\r')
utime.sleep(1)

uart.write(b'--- Directory Contents ---\n\r')
files = os.listdir()
for f in files:
    uart.write(f)
    uart.write(b' \n\r')
uart.write(b' \n\n\r')    
uart.write(b'------------------------\n\r')
utime.sleep(.5)
uart.write(b'Initialisation...\n\n\r')
uart.write(b'Initialisation du SPI0\n\r')
spi = SPI(0,baudrate=60000000,polarity=1,phase=0,bits=8,firstbit=SPI.MSB,sck=Pin(_ST7789_SCK),mosi=Pin(_ST7789_MOSI))
uart.write(str(spi))
uart.write(b'\n\r')
uart.write(b'Initialisation du LCD\n\r')
display = st7789.ST7789(spi,screen_width,screen_height,reset=Pin(_ST7789_RESET, Pin.OUT),dc=Pin(_ST7789_DC, Pin.OUT),backlight=Pin(_ST7789_BL, Pin.OUT),rotation=screen_rotation)
uart.write(b'Initialisation du FrameBuffer\n\r')

# Initialisation du FrameBuffer
# FrameBuffer needs 2 bytes for every RGB565 pixel
buffer_width = 240
buffer_height = 240
buffer = bytearray(buffer_width * buffer_height * 2)
fbuf = framebuf2.FrameBuffer(buffer, buffer_width, buffer_height, framebuf2.RGB565)
fbuf.fill(st7789.WHITE)

uart.write(b'Going Graphical!\n\r')
#---------------------------------------------------------------------------------------------------------------------
# # Définition des sous-routines
#

# class pour les flyingbox du test de l'ecran
class Box(object):
    """Bouncing box."""

    def __init__(self, screen_width, screen_height, size, display, color):
        """Initialize box.

        Args:
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
            display (framebuf): frame buffer.
            color (int): RGB565 color value.
        """
        self.size = size
        self.w = screen_width
        self.h = screen_height
        self.display = display
        self.color = color
        # Generate non-zero random speeds between -5.0 and 5.0
        seed(ticks_cpu())
        r = random() * 12.0
        self.x_speed = r - 5
        r = random() * 12.0
        self.y_speed = r - 5

        self.x = self.w / 2
        self.y = self.h / 2

        self.prev_x = self.x
        self.prev_y = self.y

    def update_pos(self):
        """Update box position and speed."""

        # update position
        self.x += self.x_speed
        self.y += self.y_speed

        # limit checking
        if self.x < 0:
            self.x = 0
            self.x_speed = -self.x_speed
        elif self.x > (self.w - self.size):
            self.x = self.w - self.size
            self.x_speed = -self.x_speed
        if self.y < 0:
            self.y = 0
            self.y_speed = -self.y_speed
        elif self.y > (self.h - self.size):
            self.y = self.h - self.size
            self.y_speed = -self.y_speed


    def draw(self):
        """Draw box."""
        x = int(self.x)
        y = int(self.y)
        size = self.size
        #self.display.rect(x, y, size, size, self.color, True ) # boite pleine
        self.display.rect(x, y, size, size, self.color, False ) # boite Vide



def TestNeoPixel(np):
# Light Show pout les NeoPixels    
    n = np.n
    np.timing = (350, 900, 800, 450) # patch des timing pour la compatibilité RP2350
    # cycle
    for i in range(6 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        time.sleep_ms(25)

    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)

    # fade in/out
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()

    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()
 
def SplashScreen():
# affiche le message du démarrage
# c'est juste pour faire cute, mais absolument inutile
    fbuf.fill(st7789.BLACK) # Efface l'écran (le framefuffer)
    fbuf.large_text('Booting', 60, 100, 2, st7789.WHITE)
    fbuf.rect(60, 140, 110, 20, st7789.WHITE, False ) # boite Vide
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)
    time.sleep(.25) # J'attends 1/4 sec
    i = 1
    while i <= 11: # animation du loading
        time.sleep(.1) # J'attends 1/4 sec
        fbuf.rect(60, 140, i*10, 20, st7789.WHITE, True ) # boite pleine
        i=i+1
        display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)
        
    time.sleep(.5) # J'attends 2 sec
    fbuf.fill(st7789.WHITE) # Efface l'écran (le framefuffer)
    # le vrai splash screen
    fbuf.large_text('DiagTools', 10, 20, 3, st7789.RED)
    fbuf.large_text('V1.0', 170, 45, 2, st7789.BLACK)
    fbuf.large_text('https://github.com/JPMichon/', 10, 70, 1, st7789.BLACK)
    fbuf.large_text("SYSTEM:", 1, 110, 1, st7789.BLUE)
    fbuf.large_text(str(os.uname().machine), 1, 120, 1, st7789.BLACK)
    fbuf.large_text("MicroPython ver:"+ str(os.uname().release), 1, 130, 1, st7789.BLACK)
    fbuf.large_text("Freq:"+ str(machine.freq()/1e6) +" Mhz", 1, 140, 1, st7789.BLACK)
    fbuf.large_text("FLASH:", 1, 165, 1, st7789.BLUE)
    fbuf.large_text("Size:" + str(int((size)/1024)) + " KB", 10, 175, 1, st7789.BLACK)
    fbuf.large_text("Used:" + str(int((size - free)/1024)) + " KB", 10, 185, 1, st7789.BLACK)
    fbuf.large_text("Free:" + str(int((free)/1024)) + " KB", 10, 195, 1, st7789.BLACK)
    fbuf.large_text('[Press AnyKey]', 5, 220, 2, st7789.BLUE)  # double size text
    
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # render display
    
def WaitInputKey():
    while BTN_Analogue.read_u16()>64000: # attend any key
        utime.sleep(.05)

def AfficheMenu(position_curseur):
    # affiche le menu de test
    fbuf.fill(st7789.BLACK) # Efface l'écran (le framefuffer)
    fbuf.rect(0, 0, 240, 35,st7789.BLUE)
    fbuf.large_text('Menu Diag', 15, 8, 3, st7789.YELLOW)
    fbuf.large_text("Ecran IPS", 30, 40, 2, st7789.WHITE)
    fbuf.large_text("Led GP25", 30, 60, 2, st7789.WHITE)
    fbuf.large_text("Scan du I2C", 30, 80, 2, st7789.WHITE)
    fbuf.large_text("EEPROM", 30, 100, 2, st7789.WHITE)
    fbuf.large_text("Piezo", 30, 120, 2, st7789.WHITE)   
    fbuf.large_text("NeoPixel", 30, 140, 2, st7789.WHITE) 
    fbuf.large_text("MicroSD", 30, 160, 2, st7789.WHITE) 
    fbuf.large_text("IO Header", 30, 180, 2, st7789.WHITE)
    fbuf.large_text("Game Of Life", 30, 200, 2, st7789.WHITE)
    fbuf.rect(0, 220, 240, 239,st7789.WHITE,True)
    fbuf.large_text("Up   Sel  Down", 10, 222, 2, st7789.BLACK)
    fbuf.large_text('>', 10, (position_curseur*20)+20, 2, st7789.CYAN)
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran

def Read_Keys():
    _read = BTN_Analogue.read_u16()
    _KeyPress='null'
    if _read < 7000: #Down
        _KeyPress='down'
    elif _read < 12000: #Select
        _KeyPress='select'
    elif _read < 16000: # Up
        _KeyPress='up'          
    #print(str(_read)) #pour le debuggage affiche la lecture de la clé dans la console    
    return _KeyPress #+str(_read) 

def SoundTest():
    Buzzer = PWM(Pin(_Buzzer)) # initialisation de la pin en PWM
    Buzzer.duty_u16(2000)
    Buzzer.freq(494)
    utime.sleep(.2)
    Buzzer.freq(440)
    utime.sleep(.2)
    Buzzer.freq(392)
    utime.sleep(.2)
    Buzzer.freq(330)
    utime.sleep(.2)
    Buzzer.freq(440)
    utime.sleep(.2)
    Buzzer.duty_u16(0)
    # permet de limité le courrant utilisé par le RP2350
    Buzzer.deinit() # de-initialize the PWM pin

def testGP25():
    System_LED.value(0) # led GP25
    for i in range(10):
        System_LED.toggle()
        utime.sleep(.2)
        
def GameofLife():
    #-------------------------------------
    # John Conway's Game of Life for the Raspberry Pi Pico Game Boy
    # based on https://github.com/YouMakeTech/Pi-Pico-Game-Boy/blob/main/GameOfLife.py
    # 
    #-------------------------------------
    # Game parameters
    WIDTH = screen_width       # screen width in pixels
    HEIGHT = screen_height      # screen height in pixels
    CELL_SIZE = 10            # width and height of cells in pixels
    CELL_RAYON=int(CELL_SIZE/2) # rayon of cells pour les cellules ronde
    POPULATION_PERCENT = 12  # Initial population size as function of total surface in %
    BACKGROUND_COLOR = st7789.BLACK
    CELL_COLOR = st7789.WHITE
    CELL_FILLCOLOR = st7789.PINK
    cellround = False # cellule carre ou ronde
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
        seed(ticks_cpu())
        board[randint(0,BOARD_SIZE_Y-1)][randint(0,BOARD_SIZE_X-1)] = CELL_COLOR
 
    # run the animation
    Boucle=1
    while Boucle==1: # attend any key
    # Update the screen
        fbuf.fill(BACKGROUND_COLOR) # Efface l'écran (le framefuffer)
        for i in range(0,BOARD_SIZE_Y):
            for j in range(0,BOARD_SIZE_X):
                if board[i][j]!=0:
                    if cellround:
                        fbuf.circle(j*CELL_SIZE,i*CELL_SIZE,CELL_RAYON,CELL_FILLCOLOR, True) #remplie la cellule en rouge
                        fbuf.circle(j*CELL_SIZE,i*CELL_SIZE,CELL_RAYON,board[i][j], False) #Trace le contour dans la couleur defini
                    else:    
                        fbuf.rect(j*CELL_SIZE,i*CELL_SIZE,CELL_SIZE,CELL_SIZE,CELL_FILLCOLOR, True) #remplie la cellule en rouge
                        fbuf.rect(j*CELL_SIZE,i*CELL_SIZE,CELL_SIZE,CELL_SIZE,board[i][j], False) #Trace le contour dans la couleur defini
                        
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
                        
                if (BTN_Analogue.read_u16()<16000): # attend anykey pour sortir de la boucle
                    Boucle=0
                    
                    
                    
def TestW5500():
    #cette sous routine teste le bon fonctionnement du module W5500
    fbuf.fill(st7789.BLACK) # Efface l'écran (le framefuffer)
    fbuf.rect(0, 0, 240, 35,st7789.BLUE)
    fbuf.large_text('NETWORK', 35, 8, 3, st7789.WHITE)
    spi=SPI(1,2_000_000, mosi=Pin(_SPI1_MOSI),miso=Pin(_SPI1_MISO),sck=Pin(_SPI1_SCK))
    nic = network.WIZNET5K(spi,Pin(_W5500_Select),Pin(_W5500_Reset)) #spi,cs,reset pin
    nic.active(True)

    if nic.isconnected():
        #nic.ifconfig(('192.168.1.6','255.255.255.0','192.168.1.1','8.8.8.8'))
        nic.ifconfig('dhcp')
        fbuf.large_text(("DHCP (Enable)"), 5, 60, 2, st7789.WHITE)
        display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
        utime.sleep(.3)
        #print(nic.ifconfig())
        IfconfigVal=nic.ifconfig()
        fbuf.large_text("IP:"+IfconfigVal[0], 20, 80, 1, st7789.YELLOW)
        fbuf.large_text("Mask:"+IfconfigVal[1], 20, 90, 1, st7789.YELLOW)
        fbuf.large_text("Network:"+IfconfigVal[2], 20, 100, 1, st7789.YELLOW)
        fbuf.large_text("DNS:"+IfconfigVal[3], 20, 110, 1, st7789.YELLOW)
        display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
        fbuf.large_text(("Ping test"), 5, 130, 2, st7789.WHITE)
        fbuf.large_text(("google.com"), 5, 155, 1, st7789.CYAN)
        display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
        n_trans, n_recv, t_elasped = uping.ping("google.com",count=4)
        fbuf.large_text(str(n_trans)+" transmitted, "+ str(n_recv)+" received", 20, 170, 1, st7789.YELLOW)
        fbuf.large_text("time="+str(t_elasped)+ " ms", 20, 190, 1, st7789.YELLOW)
    else:    
        fbuf.large_text('Cable not connected', 15, 90, 2, st7789.RED)
        
    nic.active(False)
    fbuf.large_text('[Press AnyKey]', 10, 220, 2, st7789.BLUE)  # double size text
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    WaitInputKey()
    
def TestEEPROM():
    #cette sous routine teste le bon fonctionnement du eeprom
    fbuf.fill(st7789.BLACK) # Efface l'écran (le framefuffer)
    fbuf.rect(0, 0, 240, 35,st7789.BLUE)
    fbuf.large_text('EEPROM', 45, 8, 3, st7789.WHITE)
    i2caddr=_EEPROM_ADDR #Set the I2C address of your EEPROM.
    eeprom = EEPROM_CAT24C128.CAT24C128(i2c,i2caddr)
    fbuf.large_text('Lecture:', 5, 50, 2, st7789.YELLOW)
    # Read and print 8Bytes starting from memory address 0
    _tempo=str(eeprom.read(0, 2))[-3:-1]
    fbuf.large_text(_tempo, 180, 50, 2, st7789.WHITE)
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    fbuf.large_text('Effacement', 5, 70, 2, st7789.YELLOW)
    eeprom.wipe()
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    fbuf.large_text('Lecture:', 5, 90, 2, st7789.YELLOW)
    # Read and print 8Bytes starting from memory address 0
    _tempo=str(eeprom.read(0, 2))[-3:-1]
    fbuf.large_text(_tempo, 180, 90, 2, st7789.WHITE)
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    fbuf.large_text('Ecriture', 5, 110, 2, st7789.YELLOW)
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    # Write String to memory address 0
    eeprom.write(0, 'OK')
    fbuf.large_text('Lecture:', 5, 130, 2, st7789.YELLOW)
    # Read and print 8Bytes starting from memory address 0
    _tempo=str(eeprom.read(0, 2))[-3:-1]
    fbuf.large_text(_tempo, 180, 130, 2, st7789.WHITE)
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    #fbuf.large_text('Effacement', 5, 150, 2, st7789.YELLOW)
    #eeprom.wipe()
    eeprom.write(0, 'uComp')
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    fbuf.large_text('[Press AnyKey]', 10, 220, 2, st7789.BLUE)  # double size text
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
      
    WaitInputKey() # attend que la touche AnyKey 

def TestMicroSD():
    #cette sous routine teste le bon fonctionnement de la carte microSD
    MicroSD_Detect = Pin(_MicroSD_Detect,Pin.IN)
    
    fbuf.fill(st7789.BLACK) # Efface l'écran (le framefuffer)
    fbuf.rect(0, 0, 240, 35,st7789.BLUE)
    fbuf.large_text('MicroSD', 35, 8, 3, st7789.WHITE)
    
    if MicroSD_Detect.value()==0: # si la carte est présente, j'accède a la carte  
        CS = machine.Pin(_MicroSD_Select, machine.Pin.OUT)
        spi = machine.SPI(1,baudrate=1000000,polarity=0,phase=0,bits=8,firstbit=machine.SPI.MSB,sck=machine.Pin(_SPI1_SCK),mosi=machine.Pin(_SPI1_MOSI),miso=machine.Pin(_SPI1_MISO))
        sd = sdcard.SDCard(spi,CS)
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, "/sd")
        _temp = "Size:{} MB".format(sd.sectors/2048)
        fbuf.large_text(_temp, 5, 50, 2, st7789.WHITE)
        fbuf.large_text("Create:", 5, 80, 2, st7789.WHITE)
        fbuf.large_text("uCompute.log", 20, 100, 2, st7789.YELLOW)
        display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
        # Create a file and write something to it
        with open("/sd/uCompute2.log", "w") as file:
            file.write("Welcome RP2350 uCompute World!\r\n\n")
            file.write("https://github.com/JPMichon/\r\n\n")
            file.write(b'uCompute2 system environment\n\r')
            file.write(str(os.uname().machine))
            file.write(b' @ ')
            file.write(str(int((machine.freq()/1000000))))
            file.write(b' Mhz\n\r')
            file.write(str(os.uname().version))
        fbuf.large_text("Saved", 5, 140, 2, st7789.WHITE)
        display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
           
    else:
        fbuf.large_text('Carte absente', 15, 90, 2, st7789.RED)

        
    fbuf.large_text('[Press AnyKey]', 10, 220, 2, st7789.BLUE)  # double size text
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
      
    WaitInputKey() # attend que la touche AnyKey 


def ScanI2C():
    #Inventaire des devices I2C découverte
    fbuf.fill(st7789.BLACK) # Efface l'écran (le framefuffer)
    fbuf.rect(0, 0, 240, 35,st7789.BLUE)
    fbuf.large_text('SCAN I2C', 25, 8, 3, st7789.WHITE)
    devices = i2c.scan()
    if len(devices) == 0:
        fbuf.large_text('No i2c device !', 5, 50, 2, st7789.WHITE)
    PointeurLigne=60
    for device in devices:
        fbuf.large_text('Found: ', 5, PointeurLigne, 2, st7789.WHITE)
        fbuf.large_text(str(hex(device)), 140, PointeurLigne, 2, st7789.CYAN)    
        PointeurLigne=PointeurLigne+20
        
    fbuf.large_text('[Press AnyKey]', 10, 220, 2, st7789.BLUE)  # double size text
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    # attend qu'un boutton soit enfoncé
    utime.sleep(.1)
    WaitInputKey()

def TestIO():
    #Inventaire des devices I2C découverte
    fbuf.fill(st7789.BLACK) # Efface l'écran (le framefuffer)
    fbuf.rect(0, 0, 240, 35,st7789.BLUE)
    fbuf.large_text('Test I/O', 25, 8, 3, st7789.WHITE)
    GPIO16 = Pin(16,Pin.OUT)        
    GPIO17 = Pin(17,Pin.OUT)
    GPIO18 = Pin(18,Pin.OUT)
    GPIO19 = Pin(19,Pin.OUT)
    GPIO27 = Pin(27,Pin.OUT)
    GPIO28 = Pin(28,Pin.OUT)
    fbuf.large_text("Digital out:", 10, 50, 2, st7789.YELLOW)
    fbuf.large_text("GPIO16", 30, 80, 2, st7789.WHITE)
    fbuf.large_text("GPIO17", 30, 100, 2, st7789.WHITE)
    fbuf.large_text("GPIO18", 30, 120, 2, st7789.WHITE)
    fbuf.large_text("GPIO19", 30, 140, 2, st7789.WHITE)
    fbuf.large_text("GPIO27/ADC1", 30, 160, 2, st7789.WHITE)
    fbuf.large_text("GPIO28/ADC2", 30, 180, 2, st7789.WHITE)
    fbuf.large_text('[Press AnyKey]', 10, 220, 2, st7789.BLUE)  # double size text
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # rafraichie l'écran
    
    # attend qu'un boutton soit enfoncé
    Boucle=1
    while Boucle==1: # attend any key
        GPIO16.value(0)
        GPIO17.value(0)
        GPIO18.value(0)
        GPIO19.value(0)
        GPIO27.value(0)
        GPIO28.value(0)
        utime.sleep(.1)
        GPIO16.value(1)
        GPIO17.value(1)
        GPIO18.value(1)
        GPIO19.value(1)
        GPIO27.value(1)
        GPIO28.value(1)
        utime.sleep(.1)
        if (BTN_Analogue.read_u16()<16000): # attend anykey pour sortir de la boucle
            Boucle=0
    
def TestST7789():
    #cette sous routine teste le bon fonctionnement du IPS
    # initialisation des flying box
    Nbr_boxes=25 # nombre de boites total
    boxes = [Box(buffer_width - 1, buffer_height - 1, randint(7, 50), fbuf, st7789.color565(randint(30, 256), randint(30, 256), randint(30, 256))) for i in range( Nbr_boxes )]
    Boucle=1
    fbuf.fill(0)# clear buffer
    while Boucle==1: # attend any key
        for b in boxes:
            b.update_pos()
        for b in boxes:
            b.draw()
        display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height) # render display
        fbuf.fill(0)# clear buffer
        
        if (BTN_Analogue.read_u16()<16000): # attend anykey pour sortir de la boucle
            Boucle=0
#---------------------------------------------------------------------------------------------------------------------
# Boucle principale
#
#

Pointeur_index=1

SplashScreen()# affiche le message du démarrage
WaitInputKey()# attend que la touche START soit enfoncé
AfficheMenu(Pointeur_index)#

while True:
# Boucle principale
    utime.sleep(.05) # Je ralenti la loop pour debouncer les boutons causant un déplacement ératique
    _tempo=Read_Keys() # lecture des boutons analogiques
    
#   Gestion du déplacement du curseur
    if (_tempo=="down" and Pointeur_index<Nombre_Menu):
        Pointeur_index=Pointeur_index+1
        AfficheMenu(Pointeur_index)
    elif (_tempo=="up" and Pointeur_index>1):
        Pointeur_index=Pointeur_index-1
        AfficheMenu(Pointeur_index)
        
# Gestion de l'execution des tests
    elif (_tempo=="select" and Pointeur_index==1): #test de l'affichage IPS
        utime.sleep(.1) # Je ralenti la loop pour debouncer les boutons pour eviter les reactions ératiques
        TestST7789()
        AfficheMenu(Pointeur_index)
        
    elif (_tempo=="select" and Pointeur_index==2): #test du led GP25
        testGP25()
        
    elif (_tempo=="select" and Pointeur_index==3): #test du led GP25
        ScanI2C()
        AfficheMenu(Pointeur_index) #comme le scan change l'ecran, je doit recaller l'affichage du menu au retour de la fonction
        
    elif (_tempo=="select" and Pointeur_index==4): #test du EEPROM   
        TestEEPROM()
        AfficheMenu(Pointeur_index) #comme le scan change l'ecran, je doit recaller l'affichage du menu au retour de la fonction
        
    elif (_tempo=="select" and Pointeur_index==5): #test du buzzer  
        SoundTest()
        
    elif (_tempo=="select" and Pointeur_index==6): #test NeoPixel  
        TestNeoPixel(neopixel.NeoPixel(machine.Pin(_NeoPixel), _NeoPixel_nbr))
        
    elif (_tempo=="select" and Pointeur_index==7): #test de la carteSD
        utime.sleep(.1) # Je ralenti la loop pour debouncer les boutons pour eviter les reactions ératiques
        TestMicroSD()
        AfficheMenu(Pointeur_index) #comme le scan change l'ecran, je doit recaller l'affichage du menu au retour de la fonction

    elif (_tempo=="select" and Pointeur_index==8): #test les IOs
        utime.sleep(.1) # Je ralenti la loop pour debouncer les boutons pour eviter les reactions ératiques
        TestIO()
        AfficheMenu(Pointeur_index) #comme le scan change l'ecran, je doit recaller l'affichage du menu au retour de la fonction
        
    elif (_tempo=="select" and Pointeur_index==9): #test de la carteSD
        utime.sleep(.1) # Je ralenti la loop pour debouncer les boutons pour eviter les reactions ératiques        
        GameofLife()
        AfficheMenu(Pointeur_index) #comme le scan change l'ecran, je doit recaller l'affichage du menu au retour de la fonction
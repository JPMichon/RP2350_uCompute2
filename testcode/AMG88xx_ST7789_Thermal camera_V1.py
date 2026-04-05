from machine import I2C, UART, SPI, PWM, Pin
import st7789test as st7789
import framebuf2
from amg88xx import AMG88XX
from mapper import Mapper  # Maps temperature to rgb color
import utime
import random
from math import cos, pi, sin

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

# Temperature range to cover
TMAX = 32
TMIN = 25




#Initialisation du I2C
i2c=I2C(0,sda=Pin(_I2C_SDA), scl=Pin(_I2C_SCL), freq=200000)


spi = SPI(0,baudrate=40000000,polarity=1,phase=1,bits=8,firstbit=SPI.MSB,sck=Pin(_ST7789_SCK),mosi=Pin(_ST7789_MOSI))
display = st7789.ST7789(spi,screen_width,screen_height,reset=Pin(_ST7789_RESET, Pin.OUT),dc=Pin(_ST7789_DC, Pin.OUT),backlight=Pin(_ST7789_BL, Pin.OUT),rotation=screen_rotation)

# Initialisation du FrameBuffer
# FrameBuffer needs 2 bytes for every RGB565 pixel
buffer_width = 240
buffer_height = 240
buffer = bytearray(buffer_width * buffer_height * 2)
fbuf = framebuf2.FrameBuffer(buffer, buffer_width, buffer_height, framebuf2.RGB565)
fbuf.fill(st7789.BLACK) # Efface l'écran (le framefuffer)
fbuf.large_text('Booting', 60, 100, 2, st7789.WHITE)
display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)
utime.sleep(1)
fbuf.fill(st7789.WHITE)
display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)


# Instantiate temperature sensor
i2c = machine.I2C(0)
sensor = AMG88XX(i2c)
sensor.ma_mode(False)  # Moving average mode

# Coordinate mapping from sensor to screen
invert = True  # For my breadboard layout
reflect = False
transpose = True
mapper = Mapper(TMIN, TMAX)
print('Temperature {:5.1f}°C'.format(sensor.temperature()))

# Draw color scale at right of display

val = TMIN
dt = (TMAX - TMIN) / 32
col = 60
for row in range(63, -1, -2):
    fbuf.rect(col, (row*2), 24, 6, st7789.color565(*mapper(val)),True)
    val += dt
fbuf.large_text(str(TMAX)+"C", (10), 5, 2, st7789.BLACK)
fbuf.large_text(str(TMIN)+"C", (10), 110, 2, st7789.BLACK)   
display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)    
_pixel=16 # grosseur des pixel

while True:
    sensor.refresh()  # Acquire data
    for row in range(8):
        for col in range(8):
            r = 7 - row if invert else row
            c = 7 - col if reflect else col
            if transpose:
                r, c = c, r
            val = sensor[r, c]
            fbuf.rect(((col * _pixel) +100), ((row * _pixel)+10), _pixel, _pixel, st7789.color565(*mapper(val)),True)
            #fbuf.rect(60, 140, 110, 20, st7789.WHITE, False ) # boite Vide
            #fbuf.rect(col * 8, row * 8, 8, 8,st7789.color565(*Mapper(val)))
            #ssd.fill_rect(col * 8, row * 8, 8, 8, ssd.rgb(*mapper(val)))
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)
    utime.sleep(0.01)



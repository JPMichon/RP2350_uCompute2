#
# Slideshow affichant des images BMP de 240x240 24bits sans compression sur un lcd ST7789
# Les images peuvent etre soit dans le root de la carte sd ou dans le repertoire \bmp de la memoire flash
#
from machine import I2C, UART, SPI, PWM, Pin
import st7789 as st7789
import time
import framebuf
import utime
import random
import uos
import sdcard

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
BTN_Analogue = machine.ADC(_Boutons) #Diviseur de tension des boutons
MicroSD_Detect = Pin(_MicroSD_Detect,Pin.IN) # detection de la carte SD
spi = SPI(0,baudrate=40000000,polarity=1,phase=0,bits=8,firstbit=SPI.MSB,sck=Pin(_ST7789_SCK),mosi=Pin(_ST7789_MOSI))
display = st7789.ST7789(spi,screen_width,screen_height,reset=Pin(_ST7789_RESET, Pin.OUT),dc=Pin(_ST7789_DC, Pin.OUT),backlight=Pin(_ST7789_BL, Pin.OUT),rotation=screen_rotation)

# initialisation du Framebuffer
buffer_width = 240
buffer_height = 240
buffer = bytearray(buffer_width * buffer_height * 2)
fbuf = framebuf.FrameBuffer(buffer, buffer_width, buffer_height, framebuf.RGB565)

#-------------------------------------------------------------------------------------------------------------------------------
# Routines

#Converstion d'une couleur 24bits en Color565 compatible avec le framebuffer
def color565(r, g, b):
    # same as your function:
    val16 = (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3
    # swap the bytes:
    return (val16 >> 8) | ((val16 & 0xff) << 8)

# Routine permettant de lire un fichier BMP et le copie dans le framefuffer de l'écran
def Draw_BMP(strFile):
    def lebytes_to_int(bytes):
        n = 0x00
        while len(bytes) > 0:
            n <<= 8
            n |= bytes.pop()
        return int(n)
    f = open(strFile, 'rb')
    img_bytes = list(bytearray(f.read(54)))
    x=0
    y=0
    if img_bytes:
        # Lecture du fichier BMP
        assert img_bytes[0:2] == [66, 77], "Not a valid BMP file"
        assert lebytes_to_int(img_bytes[30:34]) == 0, \
            "Compression is not supported"
        assert lebytes_to_int(img_bytes[28:30]) == 24, \
            "Only 24-bit colour depth is supported"

        start_pos = lebytes_to_int(img_bytes[10:14])
        end_pos = start_pos + lebytes_to_int(img_bytes[34:38])

        width = lebytes_to_int(img_bytes[18:22])
        height = lebytes_to_int(img_bytes[22:26])
        _pointeur = 0
        _Taille = (end_pos - start_pos) 
    while (_pointeur < _Taille):
        #pixel_data = img_bytes[start_pos:end_pos]

        for y in range(height):
            for x in range(width):
                _pointeur = _pointeur + 3
                img_bytes = list(bytearray(f.read(3)))
                r = img_bytes[0]
                g = img_bytes[1]
                b = img_bytes[2]
                CouleurPixel = color565(r, g, b)
                fbuf.pixel(y, x,CouleurPixel )  #Transpose les pixels de l'image dans le framebuffer en inversant l'axe x,y permettant une rotation de 90 deg
                #fbuf.pixel(x, y,CouleurPixel )  #Transpose les pixels de l'image dans le framebuffer
                

#----------------------------------------------------------------------
#main loop


fbuf.fill(st7789.WHITE) # Efface l'écran (le framefuffer)
fbuf.text("Loading...", 80, 120, st7789.BLACK) #Affiche un message a l'ecran
if MicroSD_Detect.value()==0: # si la carte est présente, j'affiche un message
    fbuf.text("SD CARD Present", 50, 160, st7789.BLACK)
display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)

fbuf.fill(st7789.WHITE) # Efface l'écran (le framefuffer)

directory_path = "/bmp/" # repertoire par defaut pour les fichiers bmp

if MicroSD_Detect.value()==0: # si la carte est présente, j'accède a la carte  
        CS = machine.Pin(_MicroSD_Select, machine.Pin.OUT)
        spi = machine.SPI(1,baudrate=1600000,polarity=0,phase=0,bits=8,firstbit=machine.SPI.MSB,sck=machine.Pin(_SPI1_SCK),mosi=machine.Pin(_SPI1_MOSI),miso=machine.Pin(_SPI1_MISO))
        sd = sdcard.SDCard(spi,CS)
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, "/sd") # je mount la carte SD dans le Filesystem
        directory_path = "/sd/" # je change le repertoire pour pointer sur la carte memoire
        

extension = ".bmp" # filtre pour seulement ramasser les images

txt_files_array = [file for file in uos.listdir(directory_path) if file.endswith(extension)] # je charge la liste des fichiers dans un array

#permet de changer l'orientation de l'ecran si besoin
display.rotation(0) # 0-Portrait, 1-Landscape, 2-Inverted Portrait,3-Inverted Landscape

# le slideshow en boucle
while True:
    for file in txt_files_array:
        Draw_BMP(str(directory_path+file))
        display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)



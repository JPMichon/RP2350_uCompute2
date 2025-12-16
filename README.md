# RP2350_uCompute2
Plateforme de développement basé sur un RP2350
taille: 96mm x 42mm
<BR>



## Caractéristiques:

- RP2350 
- LCD 1.3" 240x240 IPS ST7789
- EEPROM I2C (optionel)
- Bornier pour néopixel
- 1 Connecteur JST pour des modules I2C
- 3 boutons pour l'interface utilisateur (relié ADC0)
- SIP pour prototypage (8 IOs).
- Port USB (USB Mini-B ou USB-C) selon la version.
- Fusible PTC (500ma)
- Piezo
- Port MicroSD
- QSPI flash en boitier SOP8 permettant de choisir la taille (2meg - 16meg)
- DEL connecté au port standard GP25
- support pour un module Ethernet W5500
- Trous de montage 3mm
<BR>
 [!IMPORTANT] :
    le module W5500 requière environ 200ma, assurez vous d'avoir une alimentation conséquente.<BR><BR>

## Répertoires:
  Firmware: Firmware compilé en fonction des différentes configuration du SPI <BR>
  Hardware: Schématique, Gerber <BR>
  TestCode: Code Python servant d'exemple d'utilisation des différentes fonctionnalitées <BR>

## Assignation des IOs

```Python
_MicroSD_Detect = 7 # détection de la présence d'une carte MicroSD (GP7) <BR>
_MicroSD_Select = 13 # définition de la pin Select du SDCARD (GP13) <BR>
_W5500_Select = 8 # définition de la pin Select du W5500 (GP8) <BR>
_W5500_Reset = 10 # définition de la pin Reset du W5500 (GP10) <BR>
_SPI1_SCK = 14 # SPI1_shared Clock <BR>
_SPI1_MOSI = 15 # SPI1_shared MOSI <BR>
_SPI1_MISO = 12 # SPI1_shared MISO <BR>
_ST7789_SCK = 2 # définition de la pin Clock du ST7789 (GP2) SPI0 <BR>
_ST7789_MOSI = 3 # définition de la pin MOSI du ST7789 (GP3) SPI0 <BR>
_ST7789_RESET = 4 # définition de la pin Reset du ST7789 (GP4) <BR>
_ST7789_DC = 5 # définition de la pinSelect du ST7789 (GP5) <BR>
_ST7789_BL = 6 # définition de la pinBacklit du ST7789 (GP6) <BR>
_Led_System = 25 # définition du port  del systeme (GP25) <BR>
_I2C_SDA = 20 # définition de Data du I2C(0) (GP20) <BR>
_I2C_SCL = 21 # définition de SCL du I2C(0) (GP21) <BR>
_Buzzer = 11 # définition du  buzzer (GP11) <BR>
_NeoPixel = 23 # définition du port NeoPixel (GP23) <BR>
_EEPROM_ADDR = 0x50 # adresse du eeprom <BR>
_Boutons = 26 # définition du port analogue des boutons (GP26) <BR>
_UART = 0 # UART par defaut <BR>
_TX_PIN = 0 # TX Pin (GP0) <BR>
_RX_PIN = 1 # TX Pin (GP1) <BR>
```

## Rendu 3D
Revision 1.0
<img width="2369" height="1046" alt="image" src="https://github.com/user-attachments/assets/9aa6d899-e73d-40f1-a001-2d875762987e" />
<BR>
Revision 1.1
<img width="2264" height="992" alt="image" src="https://github.com/user-attachments/assets/7418f113-c4e0-4c5a-8be3-38eee2f376be" />
<BR><BR>
## BOM
Rev 1.0: 
Rev 1.1: 

## Révision
Rev 1.0: Version avec connecteur USB Mini-B  <BR>
Rev 1.1: Version avec connecteur USB Mini-C  <BR><BR>

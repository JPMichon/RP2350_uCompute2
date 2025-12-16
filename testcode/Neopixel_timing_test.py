from time import sleep
import time

GPIOPin = 23
noPixels = 8
neopixel_type=3

if not True: # your setup (True)
    from machine import Pin
    from neopixel import NeoPixel
    pin = Pin(GPIOPin, Pin.OUT)  # set GPIO0 to output to drive NeoPixels
    np = NeoPixel(pin, noPixels)
else: # my setup (not True)
    import machine
    import neopixel
    np = neopixel.NeoPixel(machine.Pin(GPIOPin), noPixels)
    np[0] = (0, 0, 0)
    np.write()
    time.sleep(1)

print('Start')

if neopixel_type == 0: np.timing = (400, 800, 850, 400)
if neopixel_type == 1: np.timing = (300, 800, 800, 300)
if neopixel_type == 2: np.timing = (300, 790, 790, 320)
if neopixel_type == 3: np.timing = (350, 900, 800, 450)

while True:
    np[0] = (64, 0, 0)
    np.write()
    print('Red')
    sleep(1)

    np[0] = (0, 64, 0)
    np.write()
    print('Green')
    sleep(1)
    
    np[0] = (0, 0, 64)
    np.write()
    print('Blue')
    sleep(1)
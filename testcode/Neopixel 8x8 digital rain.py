import machine, time
from random import random, seed, randint
from Neopixel import Neopixel

# --- Configuration ---
_NeoPixel = 23 # définition du port NeoPixel (GP23)

PIXEL_WIDTH = 8
PIXEL_HEIGHT = 8
Matrix = [[0 for j in range(PIXEL_WIDTH + 1)]for i in range(PIXEL_HEIGHT + 1)]
NUM_LEDS=PIXEL_WIDTH*PIXEL_HEIGHT # Number of LEDs in your strip
# --- Initialize NeoPixel ---

stripe = Neopixel(NUM_LEDS, 1 , _NeoPixel, "GRB")
# --- Define Colors (Matrix Green Shades) ---
GREEN_BRIGHT = (0, 80, 0)
GREEN_FADE = (0, 20, 0)
GREEN_DIM = (0, 10, 0)
BLACK = (0, 0, 0)

# --- Main Loop ---
random_number = randint(0, PIXEL_WIDTH-1)
offset=(random_number*8)
while True:
# --- Animation Function ---
    for i in range(PIXEL_HEIGHT):
        # Set a bright LED for the "drop"
        # Fade previous LEDs (or leave some as tails)
        if i>1:
            stripe[(i+offset)-1] = GREEN_FADE
        if i>2:
            stripe[(i+offset)-1] = GREEN_FADE
            stripe[(i+offset)-2] = GREEN_DIM
            
        stripe[i+offset] = GREEN_BRIGHT
        #print (i+offset)
        stripe.show() # Update the LEDs
        time.sleep_ms(20) # Adjust speed

        # Clear the trail behind the drop (optional, for cleaner single drops)
        if i>0:
            stripe[(i+offset)-1] = BLACK       
            stripe[i+offset] = BLACK
        if i>1:
            stripe[(i+offset)-2] = BLACK
            stripe[(i+offset)-1] = BLACK       
            stripe[i+offset] = BLACK            
            
        stripe.show() # Update the LEDs
    random_number = randint(0, PIXEL_WIDTH-1)
    offset=(random_number*8)
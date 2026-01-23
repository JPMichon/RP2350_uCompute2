from neopixel_matrix import NeoPixelMatrix, Color
import time

# Initialize the NeoPixel matrix
PIN = 23
np_matrix = NeoPixelMatrix(pin=PIN, width=8, height=8, direction=NeoPixelMatrix.HORIZONTAL, brightness=0.1)

# Display text on the matrix
#np_matrix.text("Hello, world!", color=Color.GREEN)
time.sleep(1)

# Scroll text on the matrix
np_matrix.scroll_text("Hello, world!", color=Color.YELLOW, delay=0.01, scroll_in=True, scroll_out=True)

# Fill the entire matrix with a specific color
np_matrix.fill(Color.BLUE)
time.sleep(1)

# Clear the matrix
np_matrix.clear()
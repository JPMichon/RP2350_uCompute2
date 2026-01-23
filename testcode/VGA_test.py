# Hugmaingauche 2025
# test file for use with the micropython VGA library
# https://github.com/HughMaingauche/PICO2-VGA-Micropython

from VGA.VGA_fonts import Font
from VGA.VGA_800x600 import screen_800x600

display = screen_800x600()
display.VGA_init()

# 3 bit color names
RED     = 0b001
GREEN   = 0b010
BLUE    = 0b100
YELLOW  = 0b011
BLACK   = 0
WHITE   = 0b111
CYAN    = 0b110
MAGENTA = 0b101

text1="L\'est s\'empourpra d\'une teinte de vieux sang et bientot \
le soleil apparut, tremblant comme un vieillard frileux. Le sol etait voile de brume ; Cugel pouvait a peine se rendre compte \
qu\'ils passaient au-dessus d\'une contree de noires montagnes et de gouffres tenebreux.\n"

display.draw_rect(1,1,display.H_res,display.V_res,GREEN)

print('Loading fonts...')

print('Loading Arial')
display.font=Font('fonts/Arial13x13.c', 13, 13)
display.settextcolor(CYAN)
display.printh("Arial13x13: ")
display.settextcolor(WHITE)
display.printh(text1+"\n")


print('Loading Calibri')
display.font=Font('fonts/Calibri12x11.c', 12, 11)
display.settextcolor(MAGENTA)
display.printh("\nCalibri12x11: ")
display.settextcolor(WHITE)
display.printh(text1+"\n")

# 
print('Loading Cascadia')
display.font=Font('fonts/Cascadia_Code7x14.c', 7, 14)
display.settextcolor(BLUE)
display.printh("\nCascadia_Code7x14: ")
display.settextcolor(WHITE)
display.printh(text1+"\n")
# 
print('Loading robotronsmall')
display.font=Font('fonts/Robotron7x11.c', 7, 11, start_letter=32, letter_count=96)
display.settextcolor(GREEN)
display.printh("ROBOTRON7X11: ")
display.settextcolor(WHITE)
display.printh(text1+"\n")
# 
print('Loading Small_Fonts7x8.c')
display.font=Font('fonts/Small_Fonts7x8.c', 7, 8, start_letter=32, letter_count=96,char_spacing=1, line_spacing=2)
display.settextcolor(RED)
display.printh("Small_Fonts7x8: ")
display.settextcolor(WHITE)
display.printh(text1+"\n")
# 
print('Loading Small_Fonts9x11.c')
display.font=Font('fonts/Small_Fonts9x11.c', 9, 11, start_letter=32, letter_count=96,char_spacing=1, line_spacing=2)
display.settextcolor(YELLOW)
display.printh("Small_Fonts9x11: ")
display.settextcolor(WHITE)
display.printh(text1+"\n")



print('Fonts loaded.')
# 
# Drawing a simple 8 color checker
for h in range(6,10):
    for i in range(0,60):
        for k in range(10):
            col=(h+k)%8
            display.draw_fastHline(k*80,k*80+80,h*60+i,col)
#
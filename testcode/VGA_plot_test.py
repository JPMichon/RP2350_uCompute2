# Micropython PICO2 VGA plot library test file
# https://github.com/HughMaingauche/PICO2-VGA-Micropython

from VGA.VGA_800x600 import screen_800x600
from VGA.VGA_plot import Plot, Line
from math import cos, pi, sin

#
# 3 bit color names
RED     = 0b001
GREEN   = 0b010
BLUE    = 0b100
YELLOW  = 0b011
BLACK   = 0
WHITE   = 0b111
CYAN    = 0b110
MAGENTA = 0b101


# Initialize VGA display
display = screen_800x600()
display.VGA_init()
display.fill_screen(BLACK)

plot1 = Plot(display, ul_x=1, ul_y=1, br_x=780, br_y=300,ax_color=WHITE, min_x=0, max_x=360, min_y=-1, max_y=1, x_ticks_num=10,y_ticks_num=10)
line1 = Line(plot1, [], [], CYAN,label="cos(x)")
line2 = Line(plot1, [], [], YELLOW,label="sin(x)")

plot2 = Plot(display, ul_x=1, ul_y=320, br_x=280, br_y=590,ax_color=GREEN, min_x=-10, max_x=10, min_y=-1, max_y=6, x_ticks_num=10,y_ticks_num=5)
line3 = Line(plot2, [], [], RED,label="cos(x) + 1/x^2") 

plot3 = Plot(display, ul_x=320, ul_y=320, br_x=770, br_y=590,ax_color=YELLOW, min_x=-30, max_x=30, min_y=-17, max_y=17, x_ticks_num=10,y_ticks_num=10)
line4 = Line(plot3, [], [], MAGENTA,label="sin(x).cos(x).x") 


for x in range(360):
    t=x*2*pi/360
    line1.add_data_ns(x,cos(t),draw_line=True)
    line2.add_data_ns(x,sin(t),draw_line=True)

for x in range(-1000,1000):
    if x!=0:
        t=x/100
        f=cos(t)+(1/t**2)
        if f<6:
            line3.add_data_ns(t,f,draw_line=True)

for x in range(-2400,2400):
    t=x/80
    f=cos(t)*sin(t)*t
    line4.add_data_ns(t,f,draw_line=True)

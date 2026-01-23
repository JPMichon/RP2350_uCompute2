# VGA simple plotter by Hugh - May 2025
from VGA.VGA_fonts import Font

# 3 bit color names
RED     = 0b001
GREEN   = 0b010
BLUE    = 0b100
YELLOW  = 0b011
BLACK   = 0
WHITE   = 0b111
CYAN    = 0b110
MAGENTA = 0b101


class Plot:
    """A two dimensionnal plot object for the VGA 800x600 display.

    Note:  All coordinates are zero based.
    """

    def __init__(self, display, ul_x=1, ul_y=1, br_x=400, br_y=300,ax_color=WHITE, min_x=0,\
                 max_x=100, min_y=0, max_y=100, x_ticks_num=10,y_ticks_num=10):
        """Initialize plot.

        Args:
            display : the VGA screen object
            ul_x,y :  upper left coordinates of the rectangle plotting area (including ticks)
            br_x,y :  bottom righy coordinates of the rectangle plotting area (including ticks)
            ax_color : color of the axes and ticks
            plot_color : color of the plot
            min_max_x_y : min/max values of the x and y axes
        """
        #set parameters
        self.display=display
        self.ul_x=ul_x
        self.ul_y=ul_y
        self.br_x=br_x
        self.br_y=br_y
        self.ax_color=ax_color
        self.min_x=min_x
        self.max_x=max_x
        self.min_y=min_y
        self.max_y=max_y
        self.x_ticks_num=x_ticks_num
        self.y_ticks_num=y_ticks_num
        # Choose defaut font here
        self.display.defaut_font=Font('fonts/Small_Fonts8x10.c', width=8, height=10,start_letter=32, letter_count=96,char_spacing=1, line_spacing=2)
        self.display.font=self.display.defaut_font
        # Define and draw plotting area (taking out space for the ticks and labels)
        self.tick_size=3
        self.top_margin=int(self.display.font.height/2)+1
        self.bottom_margin=12
        self.left_margin=20
        self.x_origin=self.ul_x+self.left_margin
        self.x_range=self.br_x-self.x_origin
        self.x_origin+=int(abs(self.x_range*(self.min_x/(self.max_x-self.min_x))))
        self.y_origin=self.br_y-self.bottom_margin
        self.y_range=self.y_origin-self.top_margin-self.ul_y
        self.y_origin-=int(abs(self.y_range*(self.min_y/(self.max_y-self.min_y))))
        self.display.draw_rect(self.ul_x+self.left_margin, self.ul_y+self.top_margin, self.br_x, self.br_y-self.bottom_margin,self.ax_color)
        self.display.settextcolor(self.ax_color)
        # prepare for legend
        self.line_labels=[]
        self.line_colors=[]
        #draw axes
        self.draw_axes_x()
        self.draw_axes_y()
        
    def draw_axes_x(self):
        # draw ticks
        for i in range(self.x_ticks_num+1):
            x_tick=self.ul_x+self.left_margin+int(i*self.x_range/self.x_ticks_num)
            self.display.draw_fastVline(x_tick,self.br_y-self.bottom_margin-self.tick_size,self.br_y-self.bottom_margin,self.ax_color)
            x_tick_val=str(round(self.min_x+(i*(self.max_x-self.min_x)/self.x_ticks_num),2))
            self.display.settextcursor(x_tick-int(self.display.strlen(x_tick_val)/2), self.br_y-self.bottom_margin+1)
            self.display.printh(x_tick_val)
            
    def draw_axes_y(self):
        # draw ticks
        for i in range(self.y_ticks_num+1):
            y_tick=self.br_y-self.bottom_margin-int(i*self.y_range/self.y_ticks_num)
            self.display.draw_fastHline(self.ul_x+self.left_margin,self.ul_x+self.left_margin+self.tick_size,y_tick,self.ax_color)
            self.display.settextcursor(self.ul_x, y_tick-int(self.display.font.height/2))
            y_tick_val=round(self.min_y+(i*(self.max_y-self.min_y)/self.y_ticks_num),2)
            self.display.printh(str(y_tick_val))

    def draw_labels(self):
        #Choose font for labels
        self.display.font=Font('fonts/Small_Fonts9x11.c', width=9, height=11, start_letter=32, letter_count=96,char_spacing=1, line_spacing=2)
        x1_line=self.x_origin+10
        for i in range(len(self.line_labels)):
            y1_line=self.top_margin+self.ul_y+int(self.display.font.width/2)+i*self.display.font.height+1
            self.display.draw_fastHline(x1_line,x1_line+10,y1_line,self.line_colors[i])
            self.display.settextcursor(x1_line+10+4, y1_line-int(self.display.font.height/2))
            self.display.settextcolor(self.line_colors[i])
            self.display.printh(self.line_labels[i])
        self.display.font=self.display.defaut_font

class Line:
    """An x.y graph object (line) for the VGA 800x600 display.

    Note:  All coordinates are zero based.
    """

    def __init__(self, plot, x_data, y_data, line_color=GREEN,label="unknown"):
        """Initialize line.

        Args:
            plot : the VGA 800x600 plot object
            x_data :  list of x values
            y_data :  list of y value
            plot_color : color of the line
        """
        #set parameters
        self.plot=plot
        self.x_data=x_data
        self.y_data=y_data
        self.x_pixdata=[]
        self.y_pixdata=[]
        self.color=line_color
        self.plot.line_labels.append(label)
        self.plot.line_colors.append(self.color)
        self.plot.draw_labels()
        self.is_first_point=True
        #draw line
        if len(self.x_data):
            self.draw()
        
    def draw(self):
        for i in range(len(self.x_data)):
            plotx=self.plot.x_origin+int((self.x_data[i]*self.plot.x_range/(self.plot.max_x-self.plot.min_x)))
            ploty=self.plot.y_origin-int((self.y_data[i]*self.plot.y_range/(self.plot.max_y-self.plot.min_y)))
            if i>0:
                self.plot.display.draw_line(self.x_pixdata[-1],self.y_pixdata[-1],plotx,ploty,self.color)
            else :
                self.plot.display.draw_pix(plotx,ploty,self.color)
            self.x_pixdata.append(plotx)
            self.y_pixdata.append(ploty)

    def add_data(self,x,y):
        if not len(self.x_data):
            plotx=self.plot.x_origin+int((x*self.plot.x_range/(self.plot.max_x-self.plot.min_x)))
            ploty=self.plot.y_origin-int((y*self.plot.y_range/(self.plot.max_y-self.plot.min_y)))
            self.plot.display.draw_pix(plotx,ploty,self.color)
            self.x_data.append(x)
            self.y_data.append(y)
            self.x_pixdata.append(plotx)
            self.y_pixdata.append(ploty)
        else:
            plotx=self.plot.x_origin+int((x*self.plot.x_range/(self.plot.max_x-self.plot.min_x)))
            ploty=self.plot.y_origin-int((y*self.plot.y_range/(self.plot.max_y-self.plot.min_y)))
            self.plot.display.draw_line(self.x_pixdata[-1],self.y_pixdata[-1],plotx,ploty,self.color)
            self.x_pixdata.append(plotx)
            self.y_pixdata.append(ploty)
            self.x_data.append(x)
            self.y_data.append(y)
 
    def add_data_ns(self,x,y,draw_line=True):
        # add_dat without storage (saves memory) 
        if self.is_first_point:
            self.plotx0=self.plot.x_origin+int((x*self.plot.x_range/(self.plot.max_x-self.plot.min_x)))
            self.ploty0=self.plot.y_origin-int((y*self.plot.y_range/(self.plot.max_y-self.plot.min_y)))
            self.plot.display.draw_pix(self.plotx0,self.ploty0,self.color)
            self.is_first_point=False
        else:
            plotx=self.plot.x_origin+int((x*self.plot.x_range/(self.plot.max_x-self.plot.min_x)))
            ploty=self.plot.y_origin-int((y*self.plot.y_range/(self.plot.max_y-self.plot.min_y)))
            if draw_line:
                self.plot.display.draw_line(self.plotx0,self.ploty0,plotx,ploty,self.color)
                self.plotx0=plotx
                self.ploty0=ploty
            else :
                self.plot.display.draw_pix(plotx,ploty,self.color)

    def add_data_moy(self,x,y,num_samples=5):
        # add_dat with mean calc over the last num_samples values
        # we only store the last num_samples value
        if not len(self.y_data):
            plotx=self.plot.x_origin+int((x*self.plot.x_range/(self.plot.max_x-self.plot.min_x)))
            ploty=self.plot.y_origin-int((y*self.plot.y_range/(self.plot.max_y-self.plot.min_y)))
            self.plot.display.draw_pix(plotx,ploty,self.color)
            for i in range(num_samples):
                self.y_data.append(y)
                self.x_pixdata.append(plotx)
                self.y_pixdata.append(ploty)
        else:
            y_last_sum=0
            for val in self.y_data:
                y_last_sum+=val
            y_mean=(y+y_last_sum)/(num_samples+1)
            y=y_mean
            plotx=self.plot.x_origin+int((x*self.plot.x_range/(self.plot.max_x-self.plot.min_x)))
            ploty=self.plot.y_origin-int((y*self.plot.y_range/(self.plot.max_y-self.plot.min_y)))
            self.plot.display.draw_line(self.x_pixdata[-1],self.y_pixdata[-1],plotx,ploty,self.color)
            self.x_pixdata.pop(0)
            self.x_pixdata.append(plotx)
            self.y_pixdata.pop(0)
            self.y_pixdata.append(ploty)
            self.y_data.pop(0)
            self.y_data.append(y)

 

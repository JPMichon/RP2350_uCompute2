from machine import Pin
from rp2 import DMA, PIO, StateMachine, asm_pio
from micropython import const
from array import array
from uctypes import addressof
from gc import mem_free,collect
from VGA.VGA_fonts import Font

class screen_800x600:
    def __init__(self):
        # VGA settings
        self.H_res=const(800)             # Horizontal resolution in pixels
        self.V_res=const(600)             # Vertical resolution in pixels
        self.bit_per_pix=const(3)         # Bits per pixel
        self.pixel_bitmask=const(0b111)   # Corresponding bitmask (used for replacing one 3bit pixel in a 32b word)
        self.usable_bits=const(30)        # Numbers of bits that will be used in each 32b word
        self.pix_per_words=const(10)     # Number of 3b pixel per 32b word
        self.SM0_FREQ=5000000   # Horizontal sync SM
        self.SM1_FREQ=150000000 # Vertical sync SM - Max freq (timings are driven by Hsync SM0 IRQ)
        self.SM2_FREQ=80000000  # Pixel clock (twice the expected because the jump loop in the PIO state machine adds a cycle)
        # Pinout
        self.H_PIN = Pin(2)
        self.V_PIN = Pin(3)
        self.RED_PIN = Pin(4,mode=Pin.ALT,alt=Pin.ALT_SIO)
        self.GREEN_PIN = Pin(5,mode=Pin.ALT,alt=Pin.ALT_SIO)
        self.BLUE_PIN = Pin(6)
        # Building the Data array buffer ###################################################################
        self.buffer_initialize()
        # Done building the Data array buffer
        # Initial text cursor position #####################################################################
        self.x_cursor = 2
        self.y_cursor = 12
        self.text_color = 0b111  # default text color WHITE
        # Loading a default font
        self.font=Font('fonts/Small_Fonts9x11.c', 9, 11, start_letter=32, letter_count=96,char_spacing=1, line_spacing=2)
        # initiate background color
        self.background_color = 0
        
    def buffer_initialize(self):
        collect()
        a0=mem_free()
        # Initiate the buffer - an array of consecutive 32bit words containing ALL the visible pixels
        self.H_buffer_line = array('L')
        # Number of required 32bit words
        visible_pix=int((self.H_res)*self.V_res*self.bit_per_pix/self.usable_bits)
        # Creating an array with all the 32b words set to zero
        for k in range(visible_pix):
            self.H_buffer_line.append(0)
        # We need an array containing the adress of the buffer for the DMA chan0 to read the values
        self.H_buffer_line_address=array('L',[addressof(self.H_buffer_line)])
        # a few information on what we just built
        a1=mem_free()
        print("mem used by buffer array (kB):\t"+str(round((a0-a1)/1024,3)))
        print("Number of 32b words:\t\t"+str(visible_pix))
        print("Number of bits (total):\t\t"+str(32*visible_pix))
        print("Number of bits (usable):\t"+str(self.usable_bits*visible_pix))
        collect()
        a0=mem_free()
        print("\nremaining RAM (kB):\t"+str(round(a0/1024,3)))


    def configure_sync(self):
        #statemachine configuration
        #sm0 is used for H sync signal
        @asm_pio(set_init=PIO.OUT_LOW, autopull=True, pull_thresh=32)
        def paral_Hsync_800():
            # ACTIVE + FRONTPORCH - Must be low and last 20 + 1 = 21 µs in 800x600 vga resolution
            set(pins, 0)                  [1] # Low for positive pulse configuration
            set(x,16)                   
            label("H_Visible")
            nop()                         [4]
            jmp(x_dec,"H_Visible")        # Remain low in active mode and front porch
            # SYNC PULSE - Must be high and last 3.2 µs in 800x600 vga resolution
            set(pins, 1)                  # high for positive pulse configuration
            nop()                         [14]
            # BACKPORCH - Must be low and last 2.2 µs in 800x600 vga resolution
            set(pins, 0)                  # Low for positive pulse configuration
            nop()                         [8]
            irq(0)                        # Set IRQ to signal end of line
            wrap()
        #     
        self.paral_write_Hsync = StateMachine(0, paral_Hsync_800,freq=self.SM0_FREQ, set_base=self.H_PIN)
        # #

        # #
        # #sm1 is used for V sync signal
        @asm_pio(sideset_init=PIO.OUT_LOW, autopull=True, pull_thresh=32)
        def paral_Vsync_600():
            wrap_target()
            # ACTIVE
            set(x,29)                     .side(0)# Setting x and y loop to match 600 lines
            label("V_active1")
            set(y,19)
            label("V_active2")
            wait(1,irq,0)                 # Wait for new Horizontal line
            irq(1)                        # Signal that we're in active mode
            jmp(y_dec,"V_active2")        # Remain in active mode, decrementing counter
            jmp(x_dec,"V_active1")        # Remain in active mode, decrementing counter
            # FRONTPORCH
            wait(1,irq,0)                    # Wait for hsync to go high Vertical Front porch is only 1 line in 800x600 resolution
            # SYNC PULSE
            set(x,3)                      .side(1)# Setting x for the loop, Vertical sync pule is 4 lines in 800x600 resolution
            label("V_syncpulse")
            wait(1,irq,0)                 # Wait for hsync to go high and Set pin low
            jmp(x_dec,"V_syncpulse")        # Remain in Syncpulse mode, decrementing counter
        #     # BACKPORCH
            set(x,24)                     .side(0)# Setting x for the loop, Vertical backporch is 23 lines in 800x600 resolution
            label("V_backporch")
            wait(1,irq,0)                 # Wait for hsync to go high and Set pin low
            jmp(x_dec,"V_backporch")        # Remain in Syncpulse mode, decrementing counter
    #         wait(1,irq,0)
            wrap()
        # 
        self.paral_write_Vsync = StateMachine(1, paral_Vsync_600,freq=self.SM1_FREQ, sideset_base=self.V_PIN)

        #sm2 is used for RGB signal
        @asm_pio(out_init=(PIO.OUT_LOW,) * 3, out_shiftdir=PIO.SHIFT_RIGHT, sideset_init=(PIO.OUT_LOW,) * 3, autopull=True, pull_thresh=self.usable_bits)
        def paral_RGB():
            pull(block)                  # Pull from FIFO to OSR (only once)
            mov(y, osr)                  # Copy value from OSR to y scratch register
            wrap_target()
            mov(x, y)                  .side(0) # Initialize counter variable + set colour pins to zero
            wait(1,irq,1)              # Wait for vsync active mode (starts 5 cycles after execution)
            label("colorout")
            out(pins,3)                # Push out to pins (one pixel)
            jmp(x_dec,"colorout")       # Stay here thru horizontal active mode
            wrap()                   
            
        self.paral_write_RGB = StateMachine(2, paral_RGB,freq=self.SM2_FREQ, out_base=self.RED_PIN,sideset_base=self.RED_PIN)
        self.paral_write_RGB.put(self.H_res-1)    # RGB loop

    def configure_DMA(self):
        ### DMA 0
        DMA1_READ_ADDRESS=const(0x5000007c) # DMA Channel 0 Write Address pointer -> DMA1 read_adress alias register 3 (CH1_AL3_READ_ADDR_TRIG ) - trigger the DMA1 start
        dma0 = DMA()
        dma0_ctrl = dma0.pack_ctrl(
            enable = True,           # enable DMA channel
            high_pri = True,        # set DMA bus traffic priority as high
            size = 2,                   # Transfer size: 0=byte, 1=half word, 2=word (default: 2)
    #         chain_to = 0,
            inc_read = False,       # do not increment to read address
            inc_write = False,      # do not increment the write address
            ring_size = 0,           # increment size is zero
            ring_sel = False,        # use ring_size
            treq_sel = 0x3f,             # select transfer rate of PIO0 TX FIFO, DREQ_PIO0_TX1
            irq_quiet = True,       # do not generate an interrupt after transfer is complete
            bswap = False,          # do not reverse the order of the word
            sniff_en = False         # do not allow access to debug
        )    

        dma0_config = dma0.config(read=self.H_buffer_line_address, write=DMA1_READ_ADDRESS, count=1, ctrl=dma0_ctrl, trigger=False)
        dma0.active(1)

        ### DMA 1
        PIO0_SM2_TXFIFO=const(0x50200018)# DMA Channel 1 Write Address pointer -> PIO TX FIFO 2 (sm2) adress
        dma1 = DMA()
        dma1_ctrl = dma1.pack_ctrl(
            enable = True,           # enable DMA channel
            high_pri = True,        # set DMA bus traffic priority as high
            size = 2,                   # Transfer size: 0=byte, 1=half word, 2=word (default: 2)
            chain_to = 0,
            inc_read = True,       # do not increment to read address
            inc_write = False,      # do not increment the write address
            ring_size = 0,           # increment size is zero
            ring_sel = False,        # use ring_size
            treq_sel = 2,             # select transfer rate of PIO0 TX FIFO, DREQ_PIO0_TX1
            irq_quiet = True,       # do not generate an interrupt after transfer is complete
            bswap = False,          # do not reverse the order of the word
            sniff_en = False         # do not allow access to debug
        )    


        dma1_config = dma1.config(read=0, write=PIO0_SM2_TXFIFO, count=len(self.H_buffer_line), ctrl=dma1_ctrl, trigger=False)
        dma1.active(1)

    def VGA_init(self):
        self.stopsync()
        self.stopdma()
        PIO(0).remove_program()
        self.configure_sync()
        self.startsync()
        self.configure_DMA()
        self.startdma()
       
    @micropython.viper
    def startsync(self):
        H=int(ptr16(self.H_res))
        ptr32(0x50200000)[0] |= 0b111    # Enable PIO0 SM 0, 1, and 2

    @micropython.viper
    def startdma(self):
        ptr32(0x50000450)[0] |= 0b00001  #triggers DMA chan0

    #     
    @micropython.viper
    def stopsync(self):
        ptr32(0x50200000)[0] &= uint(0b11111111111111111111111111111000)   # Disable PIO0 SM 0, 1 and2

    #     
    @micropython.viper
    def restart_sync(self):
        ptr32(0x50200000)[0] &= uint(0b11111111111111111111100001111111)   # Disable PIO0 SM 0, 1 and2

    @micropython.viper
    def stopdma(self):
        ptr32(0x50000464)[0] |= 0b000011         # Aborts DMA chan0 and 1
        ptr32(0x50200000)[0]

    @micropython.viper
    def draw_pix(self, x:int,y:int,col:int):
        Data=ptr32(self.H_buffer_line)
        bdisp=1<<32
        n=int((y)*(int(self.H_res)*int(self.bit_per_pix))+ (x)*int(self.bit_per_pix))
        k=(n//int(self.usable_bits)-1) if (n//int(self.usable_bits)>0)  else (int(len(self.H_buffer_line))-1)
        p=n%int(self.usable_bits)
        mask= ((int(self.pixel_bitmask) << p)^0x3FFFFFFF)
        Data[k]=(Data[k] & mask) | (col << p)

    @micropython.viper
    def fill_screen(self, col:int):
        Data=ptr32(self.H_buffer_line)
        mask=0
        for i in range(0,int(self.pix_per_words)):
            mask|=col<<(int(self.bit_per_pix)*i)
        i=0
        while i < int(len(self.H_buffer_line)):
            Data[i]=mask
            i+=1
        self.background_color=col
        

    @micropython.viper
    def draw_fastHline(self, x1:int,x2:int,y:int,col:int):
        if (x1<0):x1=0
        if (x1>(int(self.H_res)-1)):x1=(int(self.H_res)-1)
        if (x2<0):x2=0
        if (x2>(int(self.H_res)-1)):x2=(int(self.H_res)-1)
        if (y<0):y=0
        if (y>(int(self.V_res)-1)):y=(int(self.V_res)-1)
        if (x2<x1):
            temp = x1
            x1 = x2
            x2 = temp
        Data=ptr32(self.H_buffer_line)
        n1=int((y)*(int(self.H_res)*int(self.bit_per_pix))+ (x1)*int(self.bit_per_pix))
        n2=int((y)*(int(self.H_res)*int(self.bit_per_pix))+ (x2)*int(self.bit_per_pix))
        k1=(n1//int(self.usable_bits)-1) if (n1//int(self.usable_bits)>0)  else (int(len(self.H_buffer_line))-1)
        k2=(n2//int(self.usable_bits)-1) if (n2//int(self.usable_bits)>0)  else (int(len(self.H_buffer_line))-1)
        if (k2==k1):
            for i in range(x1,x2):
                self.draw_pix(i,y,col)
            return
        p1=n1%int(self.usable_bits)
        p2=n2%int(self.usable_bits)
        mask1off=0
        mask1col=0
        mask2off=0
        mask2col=0
        for i in range(p1//int(self.bit_per_pix),int(self.pix_per_words)):
            mask1off|=(int(self.pixel_bitmask))<<(int(self.bit_per_pix)*i)
            mask1col|=col<<(int(self.bit_per_pix)*i)
        mask1off^=int(0x3FFFFFFF)
        for i in range(0,p2//int(self.bit_per_pix)):
            mask2off|=(int(self.pixel_bitmask))<<(int(self.bit_per_pix)*i)
            mask2col|=col<<(int(self.bit_per_pix)*i)
        mask2off^=0x3FFFFFFF
        Data[k1]=(Data[k1] & mask1off) | mask1col
        Data[k2]=(Data[k2] & mask2off) | mask2col
        mask=0
        for i in range(0,int(self.pix_per_words)):
            mask|=col<<(int(self.bit_per_pix)*i)
        i=k1+1
        if (i>(int(len(self.H_buffer_line))-1)):i=0
        while i < k2:
            Data[i]=mask
            i+=1
        
    @micropython.viper
    def draw_fastVline(self, x:int,y1:int,y2:int,col:int):
        if (x<0):x=0
        if (x>(int(self.H_res)-1)):x=(int(self.H_res)-1)
        if (y1<0):y1=0
        if (y1>(int(self.V_res)-1)):y1=(int(self.V_res)-1)
        if (y2<0):y2=0
        if (y2>(int(self.V_res)-1)):y2=(int(self.V_res)-1)
        if (y2<y1):
            temp = y1
            y1 = y2
            y2 = temp
        Data=ptr32(self.H_buffer_line)
        n1=int((y1)*(int(self.H_res)*int(self.bit_per_pix))+ (x)*int(self.bit_per_pix))
        k1=(n1//int(self.usable_bits)-1) if (n1//int(self.usable_bits)>0)  else (int(len(self.H_buffer_line))-1)
        p1=n1%int(self.usable_bits)
        nword=(int(len(self.H_buffer_line))//int(self.V_res))
        mask= ((int(self.pixel_bitmask) << p1)^0x3FFFFFFF)
        for i in range(y2-y1):
            Data[k1+i*nword]=(Data[k1+i*nword] & mask) | (col << p1)

    def draw_line(self, x1,y1,x2,y2,col):
        if (x1<0):x1=-1
        if (x1>(int(self.H_res)-1)):x1=(int(self.H_res))
        if (x2<0):x2=-1
        if (x2>(int(self.H_res)-1)):x2=(int(self.H_res))
        if (y1<0):y1=-1
        if (y1>(int(self.V_res)-1)):y1=(int(self.V_res))
        if (y2<0):y2=-1
        if (y2>(int(self.V_res)-1)):y2=(int(self.V_res))
        if (x1==x2):
            self.draw_fastVline(x1,y1,y2,col)
        else:
           a=(y2-y1)/(x2-x1)
           b=y1-a*x1
           x=x1
           while (x<=x2):
               self.draw_pix(x,int(x*a+b),col)
               x+=1

    @micropython.viper
    def fill_rect(self, x1:int,y1:int,x2:int,y2:int,col:int):
        j=int(min(y1,y2))
        while (j<int(max(y1,y2))):
            self.draw_fastHline(x1,x2,j,col)
            j+=1

    @micropython.viper
    def draw_rect(self, x1:int,y1:int,x2:int,y2:int,col:int):
        self.draw_fastHline(x1,x2,y1,col)
        self.draw_fastHline(x1,x2,y2,col)
        self.draw_fastVline(x1,y1,y2,col)
        self.draw_fastVline(x2,y1,y2,col)

    @micropython.viper
    def draw_circle(self, x:int, y:int, r:int , color:int):
        if (x < 0 or y < 0 or x >= int(self.H_res) or y >= int(self.V_res)):
            return
        # Bresenham algorithm
        x_pos = 0-r
        y_pos = 0
        err = 2 - 2 * r
        while 1:
            self.draw_pix(x-x_pos, y+y_pos,color)
            self.draw_pix(x-x_pos, y-y_pos,color)
            self.draw_pix(x+x_pos, y+y_pos,color)
            self.draw_pix(x+x_pos, y-y_pos,color)
            e2 = err
            if (e2 <= y_pos):
                y_pos += 1
                err += y_pos * 2 + 1
                if((0-x_pos) == y_pos and e2 <= x_pos):
                    e2 = 0
            if (e2 > x_pos):
                x_pos += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break

    @micropython.viper
    def fill_disk(self, x:int, y:int, r:int , color:int):
        if (x < 0 or y < 0 or x >= int(self.H_res) or y >= int(self.V_res)):
            return
        # Bresenham algorithm
        x_pos = 0-r
        y_pos = 0
        err = 2 - 2 * r
        while 1:
            self.draw_fastHline(x-x_pos,x+x_pos,y+y_pos,color)
            self.draw_fastHline(x-x_pos,x+x_pos,y-y_pos,color)
            e2 = err
            if (e2 <= y_pos):
                y_pos += 1
                err += y_pos * 2 + 1
                if((0-x_pos) == y_pos and e2 <= x_pos):
                    e2 = 0
            if (e2 > x_pos):
                x_pos += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break
           
    def settextcursor(self, x,y):
        self.x_cursor = x
        self.y_cursor = y

    def settextcolor(self, color):
        self.text_color = color

    def printh(self, mess):
        for i in mess:
            if i=="\n":
                self.x_cursor=2
                self.y_cursor = self.y_cursor+self.font.height+self.font.line_spacing
            else:
                self.drawchar(i)
                if self.x_cursor>(self.H_res-self.font.width):
                    self.x_cursor=2
                    self.y_cursor = self.y_cursor+self.font.height+self.font.line_spacing
            if (self.y_cursor>(self.V_res-self.font.height)):
                self.x_cursor=2
                self.y_cursor=self.font.height
                self.fill_screen(self.background_color)

    def strlen(self,mess):
        pixel_count=0
        for char in mess:
            pixel_count+=self.font.Get_letter(char)[0]
        return pixel_count
        
    def drawchar(self,char):
        letter=self.font.Get_letter(char)
        W=letter[0]
        H=self.font.height if not (self.font.height%8) else (8*(self.font.height//8+1))
        ypos=1
        x=self.x_cursor
        y=self.y_cursor
        for a in letter[1:]:
            if ((x-self.x_cursor) >= W):
                break
            for i in range(8):
                if (a & (1<<i)) :
                    self.draw_pix(x,y,self.text_color)
                y+=1
                ypos+=1
                #print("pos=",pos,"\tx=",x,"\ty=",y)        
                if (ypos>(H)):
                    y=self.y_cursor
                    x+=1
                    ypos=1        
        self.x_cursor+=W
        self.x_cursor+=self.font.char_spacing

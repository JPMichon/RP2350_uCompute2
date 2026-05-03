from machine import UART, Pin, SPI
import time
import math
import struct
import st7789
import framebuf2
from SECRET import _SSID, _WifiPWD

# --- CONFIGURATION ---
CONFIG = {
    "screen_w": 240,
    "screen_h": 240,
    "center_x": 120,
    "center_y": 120,
    "radius": 110,
    "ntp_server": "pool.ntp.org",
    "gmt_offset": -4 * 3600,
    "colors": {
        "BG": st7789.BLACK,
        "DIAL": st7789.WHITE,
        "HOUR": st7789.WHITE,
        "DateBox": 0x45b0, #STEELBLUE
        "DateBox_border": 0xff1f, #LIGHTYELLOW
        "MIN": 0x7BEF, # Gris clair
        "SEC": 0xF800, # Rouge
        "NTP": 0x7BEF, # Gris clair
        "TXT": st7789.WHITE  # 
    }
}

class UCompute:
    def __init__(self):
        self.spi = SPI(0, baudrate=40000000, polarity=1, phase=1, sck=Pin(2), mosi=Pin(3))
        self.display = st7789.ST7789(
            self.spi, 240, 240,
            reset=Pin(4, Pin.OUT), dc=Pin(5, Pin.OUT), 
            backlight=Pin(6, Pin.OUT), rotation=1
        )
        self.buffer = bytearray(240 * 240 * 2)
        self.fbuf = framebuf2.FrameBuffer(self.buffer, 240, 240, framebuf2.RGB565)
        
        self.esp_en = Pin(12, Pin.OUT)
        self.esp_rst = Pin(10, Pin.OUT)
        self.uart = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))

    def refresh(self):
        self.display.blit_buffer(self.buffer, 0, 0, 240, 240)

class ESPManager:
    def __init__(self, hw):
        self.hw = hw
        self.uart = hw.uart

    def boot(self):
        self.hw.esp_rst.value(0)
        time.sleep(0.5)
        self.hw.esp_rst.value(1)
        self.hw.esp_en.value(1)
        time.sleep(2)

    def send_at(self, cmd, timeout=3000, expected="OK"):
        self.uart.write(cmd + "\r\n")
        start = time.ticks_ms()
        resp = b""
        while (time.ticks_ms() - start) < timeout:
            if self.uart.any():
                resp += self.uart.read()
                try:
                    if expected in resp.decode('utf-8', 'ignore'): return True
                except: pass
        return False

    def connect_wifi(self, ssid, pwd):
        self.send_at("AT+CWMODE=1")
        return self.send_at(f'AT+CWJAP="{ssid}","{pwd}"', timeout=10000)

    def get_ntp_time(self, server):
        self.send_at(f'AT+CIPSTART="UDP","{server}",123')
        if self.send_at("AT+CIPSEND=48"):
            self.uart.write(b'\x1b' + 47 * b'\0')
            time.sleep(1)
            raw = self.uart.read()
            if raw:
                try:
                    idx = raw.find(b':') + 1
                    return struct.unpack(">I", raw[idx:][40:44])[0] - 2208988800
                except: pass
        return None

def draw_analog_clock(hw, t):
    f = hw.fbuf
    c = CONFIG["colors"]
    cx, cy = CONFIG["center_x"], CONFIG["center_y"]
    r = CONFIG["radius"]

    f.fill(c["BG"])

    # 1. Dessiner le cadran (graduations)
    for i in range(12):
        angle = math.radians(i * 30)
        x1 = int(cx + (r - 10) * math.sin(angle))
        y1 = int(cy - (r - 10) * math.cos(angle))
        x2 = int(cx + r * math.sin(angle))
        y2 = int(cy - r * math.cos(angle))
        f.line(x1, y1, x2, y2, c["DIAL"])

    # Extraire Heures, Minutes, Secondes
    hh, mm, ss = t[3], t[4], t[5]
    
    # Date sur le côté "Montre de luxe"
    f.fill_rect(cx+40, cy-9, 50, 16, c["DateBox"]) #petite boite pour la date
    f.rect(cx+40, cy-9, 50, 16, c["DateBox_border"]) #petite boite pour la date
    date_str = "{:02d}/{:02d}".format(t[2], t[1])
    f.large_text(date_str, cx+45, cy-5, 1, c["TXT"])
    
    # 2. Aiguille des Heures (Courte et épaisse)
    h_angle = math.radians((hh % 12) * 30 + mm * 0.5)
    hx = int(cx + (r * 0.5) * math.sin(h_angle))
    hy = int(cy - (r * 0.5) * math.cos(h_angle))
    f.line(cx, cy, hx, hy, c["HOUR"])
    f.line(cx+1, cy, hx+1, hy, c["HOUR"]) # Épaisseur simulée

    # 3. Aiguille des Minutes (Longue)
    m_angle = math.radians(mm * 6)
    mx = int(cx + (r * 0.8) * math.sin(m_angle))
    my = int(cy - (r * 0.8) * math.cos(m_angle))
    f.line(cx, cy, mx, my, c["MIN"])

    # 4. Aiguille des Secondes (Fine et Rouge)
    s_angle = math.radians(ss * 6)
    sx = int(cx + (r * 0.9) * math.sin(s_angle))
    sy = int(cy - (r * 0.9) * math.cos(s_angle))
    f.line(cx, cy, sx, sy, c["SEC"])

    # 5. Moyeu central
    f.fill_rect(cx-2, cy-2, 4, 4, c["DIAL"])
    
  
    
    # affichage du serveru NTP
    f.large_text(CONFIG["ntp_server"], cx-45, cy+40, 1, c["NTP"])
    hw.refresh()

def main():
    hw = UCompute()
    esp = ESPManager(hw)
    
    hw.fbuf.fill(st7789.BLACK)
    hw.fbuf.large_text("SYNCING...", 70, 110, 1, st7789.WHITE)
    hw.refresh()
    
    esp.boot()
    if esp.connect_wifi(_SSID, _WifiPWD):
        ntp_sec = esp.get_ntp_time(CONFIG["ntp_server"])
        if ntp_sec:
            offset = (ntp_sec + CONFIG["gmt_offset"]) - time.time()
            while True:
                t = time.localtime(time.time() + int(offset))
                draw_analog_clock(hw, t)
                time.sleep(1)

if __name__ == "__main__":
    main()
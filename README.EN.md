# **:computer: RP2350 uCompute2**

## [Version Francaise ici](./README.md)


The **RP2350 uCompute2** is an autonomous, highly modular embedded development platform based on the **Raspberry Pi Pico RP2350** microcontroller. Designed as an all-in-one hardware solution, it integrates expanded storage, versatile display interfaces, and an ecosystem of interchangeable daughterboards (Ethernet, WiFi, Radio, VGA), making it ideal for complex embedded projects, network prototyping, and education.
The board offers a dual software approach: it can be programmed and used exactly like a standard Raspberry Pi Pico, or run the custom GUI (uComputeOS) designed for this platform. Written in MicroPython, this mini-operating system provides an interactive graphical interface to browse, copy, and dynamically execute scripts stored in the QFlash memory or on the Micro SD card.

>[!NOTE]
>For the sharp-eyed among you, the **RP2350 uCompute2** is an evolution of my previous **[RP2040 uCompute](https://github.com/JPMichon/RP2040_uCompute)** project. These two projects share the same DNA; therefore, the modules are interchangeable and, as a general rule, the **MicroPython** code is compatible between both systems. However, since the microcontroller is different, it goes without saying that you cannot reuse a firmware compiled for the **RP2040**, as it will not run on the **RP2350**.
><br>

<img width="703" height="314" alt="image" src="https://github.com/user-attachments/assets/fe666037-9144-4d45-a901-445b3db0c9fb" />

_Size: 96mm x 42mm_ <BR>

---

## 🛠️ Manufacturing & Assembly (Do It Yourself)

This project is licensed under **CC BY-NC-SA 4.0**. The **Gerber files** as well as the Bill of Materials (BOM) are available in the Hardware/ folder. You are free to have the PCBs manufactured by the vendor of your choice.

⚠️ **Technical Skill Required:** Manually assembling the original PCB requires **advanced expertise in SMD (Surface Mount Device) soldering.** The main microcontroller ideally requires the use of a hot air rework station or a heating plate.

💡 **Prototyping Alternative:** If you do not wish to solder surface-mount components, please note that using the provided schematics, it is entirely possible to build a functional prototype using a **breadboard or protoboard**. You will simply need to use a **standard Raspberry Pi Pico (RP2040) or Pico 2 (RP2350) module** and wire the components (screen, SD reader, etc.) to the corresponding logical GPIOs.

---

# 🤖 AI Coding Assistants

If you are using an AI agent (such as ChatGPT, Claude, or GitHub Copilot) to help you develop on the **RP2350 uCompute2**, configure it instantly by copying and pasting one of our custom profiles. The AI will immediately know all the pin definitions and exact board addresses to write code without any hardware errors!

💼 **[uCompute Freelance Developer Mode Designed](UCompute_FreelanceCoder.md)** for efficiency and speed. The AI acts as a senior programmer at your service: you explain your concept or specifications, and it delivers a complete, optimized script that is immediately ready to be copied and pasted.

---

## 🛠️ The technical specifications include:
• RP2350<br>
• 1.3" 240x240 IPS ST7789 LCD<br>
• CAT24Cxx I2C EEPROM (optional)<br>
• Terminal block for NeoPixel<br>
• 1 JST connector for I2C modules<br>
• 3 buttons for user interface (connected to ADC0)<br>
• SIP for prototyping (10 IOs)<br>
• USB port (USB Mini-B or USB-C) depending on the version<br>
• PTC fuse (500mA)<br>
• Piezo buzzer<br>
• MicroSD card reader<br>
• QSPI flash in SOP8 package, allowing you to choose the size (2MB - 16MB)<br>
• LED connected to the standard GP25 pin<br>
• Support for a W5500 Ethernet module<br>
• 3mm mounting holes<br>
• Dimensions: 96mm x 42mm<br>
<br>

---

### The IOs Terminal Block (1x14 Pin Header)
The pin header block facilitates prototyping. It features a standard 2.54 mm spacing, allowing it to be plugged into a prototyping board (Protoboard) or connected using jumper wires with Dupont connectors to link your circuits or modules.

### Power & Signals
• **5V** (Direct power supply from the USB, ideal for power-hungry components)<br>
• **3.3V** (Regulated via the AP2114H-3.3TRG1)<br>
• **GND** (Common ground)<br>
• **UART 0**: GP0 (TX) & GP1 (RX)<br>
• **2 Analog Inputs (ADC)**: GP27 (ADC1) & GP28 (ADC2)<br>
• **6 Digital Pins (GPIO)**: GP16, GP17, GP18, GP19, GP22, GP24<br>
<BR>

> [!CAUTION]
>**The RP2350 is 5V tolerant. BUT...**
> The IOVDD power rail must absolutely be powered (at 3.3V) as soon as a **5V** signal is applied to a GPIO pin. If a 5V signal is sent to a pin while the RP2350's IOVDD is turned off or tied to ground, the pin will suffer irreversible electrical damage.<br>
>**Analog pins do NOT tolerate 5V**
The **5V** tolerance applies only to purely digital GPIO pins. Pins that share their function with the analog inputs of the converter (the ADC channels) do not have this protection and will be destroyed if exposed to **5V**.

<br>
##🔌 Alternative 5V Power Supply

The most common way to power the circuit is through the USB connector. However, it is possible to power the circuit with **5V** from pin 1 of the NeoPixel connector or via **pin 1** of the extension terminal block. Diode **D1** protects the USB port from reverse current, but it is always preferable to disconnect the external **5V** power supply when connecting the circuit to a computer.

> [!WARNING]
>The absolute Vin of the AP2114H-3.3TRG1 regulator is 6.5V, so the **maximum is 5.5V.**

---

## IO Assignment
```Python
# Pin configuration for AI Coding Assistants & MicroPython
# Based on the uCompute and uCompute2 schematics

_MicroSD_Detect = 9   # Definition of the MicroSD card presence (GP9)
_MicroSD_Select = 5   # Definition of the SD reader Select pin (GP5)

_w5500_Select   = 6   # Definition of the W5500 Select pin (GP6)
_w5500_Reset    = 7   # Definition of the W5500 Reset pin (GP7)

_SPI1_SCK       = 4   # Shared SPI_SCK (GP4)
_SPI1_MOSI      = 3   # Shared SPI_MOSI (GP3)
_SPI1_MISO      = 2   # Shared SPI_MISO (GP2)

_st7789_SCK     = 10  # Definition of the ST7789 Clock pin (GP10)
_st7789_MOSI    = 11  # Definition of the ST7789 MOSI pin (GP11)
_st7789_RESET   = 12  # Definition of the ST7789 Reset pin (GP12)
_st7789_DC      = 13  # Definition of the ST7789 DC pin (GP13)
_st7789_BL      = 14  # Definition of the ST7789 Backlight pin (GP14)

_Led_System     = 25  # Definition of the system LED port (GP25)

_I2C_SDA        = 21  # Definition of I2C(0) Data (GP21)
_I2C_SCL        = 20  # Definition of I2C(0) SCL (GP20)

_Buzzer         = 15  # Definition of the buzzer (GP15)
_NeoPixel       = 23  # Definition of the NeoPixel port (GP23)

_EEPROM_ADDR    = 0x50 # I2C EEPROM Address

_Boutons        = 26  # Definition of the buttons analog port (GP26 / ADC0)

_UART           = 0   # Default UART
_TX_PIN         = 0   # TX Pin (GP0)
_RX_PIN         = 1   # RX Pin (GP1)

```

---

## 🔌 Extension Modules Ecosystem (Add-ons)
The dual-row rear socket and the front display connector form a standardized expansion port, allowing the hardware to be tailored to the target application.
All modules from the **uCompute series** are compatible with the **RP2350 uCompute2**. Modules are available in the other depot [RP2040 uCompute](https://github.com/JPMichon/RP2040_uCompute/tree/main/Modules).

### 1. Communication Modules (Rear Socket)
The mechanical and electrical footprint is compatible with several interchangeable technologies:

* **Ethernet Module (W5500)**: Provides stable wired network connectivity over SPI (requires a specific firmware).<br>
_Commercially available from multiple third-party vendors._<br>
<img width="221" height="288" alt="image" src="https://github.com/user-attachments/assets/b017c095-deda-49ad-ae25-3661ce4e3009" /><br>
* **WiFi Module (ESP-12F)**: Adapter board featuring an ESP8266 module to add Wi-Fi connectivity.<br>
<img width="203" height="266" alt="image" src="https://github.com/user-attachments/assets/f0c80621-1b07-46e6-844b-4594e3d338f9" /><br>
* **Radio Module (NRF24L01 - GT-24 Mini.MK1)**: Adapter equipped with a 2x4 female pin header for low-power, point-to-point radio links (2.4 GHz).<br>
<img width="226" height="277" alt="image" src="https://github.com/user-attachments/assets/a6a0a83b-80ed-4dbc-bc28-06579f64b54c" />

---

### 2. Display & Video Module (Front Socket)
• **µCompute VGA8 Adaptor (REV 1.0)**: Connects in place of the ST7789 LCD screen to generate and export an analog video signal to a standard monitor via a **VGA (DE-15) port**.

<img width="343" height="292" alt="image" src="https://github.com/user-attachments/assets/a070a613-6fbb-4731-9103-bb9ae0ae5e83" />

---

## 🎓 Accessibility & Compatibility with the Raspberry Pi Pico

If you are new to programming or electronics, don't be intimidated! Although the **RP2350 uCompute2** integrates many components onto a single printed circuit board (VGA, Wi-Fi, MicroSD, etc.), **its core remains a standard Raspberry Pi Pico 2**.
There are actually **very few fundamental differences** between this board and a classic Pi Pico:
• **Same chip**: The main microcontroller is the RP2350. Any code written for a standard Pico will work here.
• **Same foundations**: The programming logic, pin usage (GPIO), and environment remain identical.

### 📚 Resources for Beginners

Since the architecture is the same, you can fully use official Raspberry Pi Foundation guides, tutorials, and documentations to learn how to program your **RP2350 uCompute2.**
To take your first steps, I highly recommend the official guide:
👉 **[Getting started with the Raspberry Pi Pico (Raspberry Pi Projects)](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico)**

This guide will teach you step-by-step how to:
1. Install and configure the **Thonny development environment**.
2. Connect your board to your computer and install the **MicroPython firmware**.
3. Write your first scripts to control inputs and outputs.
Once you have mastered the basics of blinking an LED or reading a button using this guide, the **RP2350 uCompute2** ecosystem and its test scripts (testcode/) will allow you to go much further (graphical display, sound, games, and networking) without changing your workflow!
<br>

## 💾 Software Section: uComputeOS

The board runs **uComputeOS**, a mini embedded operating system written in MicroPython.

### Hardware dependencies to include (`lib/` folder):
* **LCD Screen Version:** `st7789py.py`, `framebuf2.py`, `vga1_8x8.py`, `vga2_bold_16x16.py`
* **OLED Screen Version:** `ssd1306.py`
* **Common Storage:** `sdcard.py`

### Major features of uComputeOS:
1. **Splash Screen:** Displays system information (`os.uname`), firmware version, as well as total and free Flash space calculated live.
2. **File Manager (FileManager):** Dynamically detects at boot if a Micro SD card is present. The user selects their root storage space (`FLASH` or `SD`).
3. **Navigation & Selection:** Visual interface navigable using the analog button (`Up`, `Down`, `Select`). A triangle-shaped cursor points to the selected script.
4. **Dynamic Execution (`EXEC`):** Allows opening any user `.py` file present on the storage medium and executing it on the fly. In case of a code error, uComputeOS captures the exception and displays a red error screen without crashing the board.
5. **Inter-Storage Copying (`CP>SD` / `CP>\`):** Integrates a block-based copy function (512 bytes) allowing scripts to be transferred from the internal Flash memory to the SD card (and vice versa) directly from the hardware interface.

### ⚙️ Automatic Execution at Boot (Configuration in `main.py`)

For the graphical interface (**uComputeOS**) to launch automatically upon powering up the board without requiring a computer, you must register it as the main script:

1. **Select the version** of the code corresponding to your hardware configuration (ST7789 LCD Screen Version or SSD1306 OLED Screen Version).
2. **Rename the chosen file** to **`main.py`**.
3. **Transfer it to the root** of the RP2040's internal Flash memory (and not in the `lib/` folder) using your IDE (such as Thonny).
4. **Ensure** that all required dependencies (`sdcard.py`, screen drivers, and fonts) are present in the `/lib` folder of the internal memory.

On the next reboot or power cycle, the MicroPython firmware will natively look for the `main.py` file and instantly boot the GUI on the screen.

---

## 📜 License

The hardware (design files, schematics, layouts) and software of this project are made available under the terms of the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

❌ **Commercial use of this project (reselling bare PCBs, kits, or assembled retroPico boards) is strictly prohibited without prior authorization from the author.**

Check the [LICENSE](LICENSE) file to read the full terms.

---

## ☕ Support the Project

If you appreciate my work and would like to **buy me a coffee** to support my future soldering and coding projects, you can leave a [**tip on Ko-fi** ](https://ko-fi.com/jpmichon) This is completely voluntary and greatly appreciated!

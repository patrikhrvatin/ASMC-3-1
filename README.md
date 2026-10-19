# ASMC 1-3 (Advanced StackMatch Controller)

**ASMC 1-3** is an advanced, microcontroller-driven antenna stack controller based on the **Arduino Nano (ATmega328P)** module and an interactive **Python GUI** interface. It is designed for demanding amateur radio environments with a strong focus on reliability, hardware safety, and operational flexibility.

---

## 🚀 Key Features

* **Bi-directional USB Communication:** Synchronized real-time status management and monitoring between the hardware and the PC.
* **Dual Operating Modes (RX/TX):** 
  * **Exclusive Mode (EXCL):** Allows listening to only one selected antenna at a time.
  * **Flexible Mode (FLEX):** Allows free combination and simultaneous selection of multiple antennas.
* **Advanced PTT Interlock Protection:** Software and hardware lockout preventing hot-switching under high RF power.
* **Automatic Matching (Relay 4):** Independent activation of the wideband matching transformer when using two or three active antennas simultaneously.
* **Fail-Safe Safety Logic:** In case of power loss or system failure, the hardware automatically defaults to all antennas connected ($A+B+C$) via NC (Normally Closed) relay contacts.
* **Visual LED Indication:** Status LEDs featuring a PWM fade ("breathing") effect during transmission.
* **Built-in Watchdog Timer:** Automatically resets the microcontroller in case of any software freeze.

---

## 📌 Pinout (Arduino Nano)

| Arduino Pin | Code Label | Function |
| :--- | :--- | :--- |
| **Pin 2 (D2)** | `RELAY_1` | Control output for Relay 1 (Antenna A / TOP) |
| **Pin 3 (D3)** | `RELAY_2` | Control output for Relay 2 (Antenna B / MID) |
| **Pin 4 (D4)** | `RELAY_3` | Control output for Relay 3 (Antenna C / BOT) |
| **Pin 5-7** | `BTN_RX_A/B/C` | Physical pushbuttons for RX antenna selection |
| **Pin 8-10** | `BTN_TX_A/B/C` | Physical pushbuttons for TX antenna profile selection |
| **Pin 11 (D11)** | `PTT_PIN` | PTT input via optocoupler (`LOW` = transmit) |
| **Pin 12-13** | `BTN_RX/TX_ALL`| Pushbuttons for quick selection of all antennas ($A+B+C$) |
| **Pin A0-A2** | `LED_RX_A/B/C` | Status LEDs for receive |
| **Pin A3, A6, A7** | `LED_TX_A/B/C` | PWM status LEDs for transmit |
| **Pin A4** | `BTN_RX_MODE` | Pushbutton to toggle RX mode (EXCL / FLEX) |
| **Pin A5** | `RELAY_4` | Control output for Relay 4 (Wideband Transformer) |

---

## 🛠️ Repository Structure

```text
ASMC-1-3/
│
├── arduino/
│   └── stack_match_usb2.ino      # Arduino Nano source code
│
├── software/
│   └── asmc_gui.py               # Python graphical user interface (GUI)
│
└── SCHEMATICS.md                 # Detailed wiring schematics and instructions

⚙️ Setup & Installation
1. Arduino Firmware

    Open the stack_match_usb2.ino project in Arduino IDE (recommended version 1.8.19).

    Select board: Arduino Nano with processor ATmega328P.

    Ensure the library #include <avr/wdt.h> is included.

    Upload the code to the Arduino Nano.

2. Python GUI Interface

    Ensure Python and required libraries (e.g., pyserial, tkinter) are installed.

    Run the application:
python asmc_gui.py
Select the appropriate COM port and click Connect.

📄 License

This project is developed for amateur radio use. Feel free to use, upgrade, and adapt it to your needs.

73!


# DIY Litter Robot Controller (ESP32)

This project replaces the original circuit board of a Litter Robot with an **ESP32 Microcontroller** and an **L298N Motor Driver**. It provides WiFi connectivity and a web interface to monitor status and manually trigger cycles.

## Features
*   **Automatic Cleaning Cycle:** Detects cat, waits 7 minutes, then cycles.
*   **Safety Interrupt:** If the cat enters during a cycle, the motor stops immediately.
*   **Web Interface:** Monitor status ("IDLE", "WAITING", "CYCLING") and manually trigger/stop cycles from your phone/browser.
*   **WiFi Connected:** Connects to your home network.

## Hardware Requirements
See [WIRING.md](WIRING.md) for the detailed wiring diagram.
*   ESP32 Development Board
*   L298N Motor Driver Module
*   Buck Converter (12V -> 5V)
*   Original Litter Robot Motor & Sensors (or replacements)

## Installation Logic
1.  **Install Arduino IDE:** Download and install the Arduino IDE.
2.  **Install ESP32 Board Manager:**
    *   Go to `File` -> `Preferences`.
    *   Add `https://dl.espressif.com/dl/package_esp32_index.json` to "Additional Board Manager URLs".
    *   Go to `Tools` -> `Board` -> `Boards Manager`, search for "esp32", and install.
3.  **Configure Code:**
    *   Open `litter_robot_controller.ino`.
    *   Update `ssid` and `password` with your WiFi credentials.
    *   Verify the Pin definitions match your wiring.
4.  **Upload:**
    *   Select your board (e.g., "DOIT ESP32 DEVKIT V1") in `Tools` -> `Board`.
    *   Connect the ESP32 via USB.
    *   Click Upload.

## Usage
1.  Power on the Litter Robot.
2.  The ESP32 will connect to WiFi. Open the Serial Monitor (115200 baud) to see the assigned IP address.
3.  Type that IP address into your web browser.
4.  You should see the status page.

## Troubleshooting
*   **Motor moving wrong way:** Swap the `IN1` and `IN2` pin definitions in the code OR swap the motor wires at the driver.
*   **Sensors not working:** Check if your sensors need pull-up resistors. The code uses `INPUT_PULLUP` for the cat and home sensors, but GPIO 35 (Dump sensor) on some ESP32 boards is input-only without internal pull-ups. You might need to add an external 10k resistor from the pin to 3.3V.

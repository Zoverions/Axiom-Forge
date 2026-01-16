# DIY Litter Robot Controller (Arduino Nano)

This project replaces the original circuit board of a Litter Robot (Model II or similar) with an **Arduino Nano**, **L298N Motor Driver**, and **LM2596 Buck Converter**.

## Features
*   **Automatic Cleaning Cycle:** Detects cat, waits 7 minutes, then cycles (Rotate to Dump -> Pause -> Rotate Home).
*   **Safety Interrupt:** If the cat enters during a cycle, the motor reverses and stops.
*   **Manual Controls:** Support for optional Cycle, Empty, and Fill buttons.
*   **Status LEDs:** Support for Green (Ready), Yellow (Cycling), and Red (Error) LEDs.

## Hardware Requirements
See [WIRING.md](WIRING.md) for the detailed wiring diagram.

### Components
*   **Microcontroller:** Arduino Nano (ATmega328P).
*   **Motor Driver:** L298N Dual H-Bridge Module.
*   **Power Supply:** Original 15V DC Adapter.
*   **Regulation:** LM2596 DC-DC Buck Converter (15V -> 5V).
*   **Sensors:** Original Hall Effect sensors (Home/Dump) and Cat Weight Sensor.

## Installation Logic
1.  **Install Arduino IDE:** Download and install the Arduino IDE.
2.  **Configure Code:**
    *   Open `litter_robot_controller.ino`.
    *   Verify the `CURRENT_THRESHOLD` matches your motor's characteristics if using current sensing.
    *   Adjust `ROTATION_TIMEOUT` if your cycle takes longer than 60 seconds.
3.  **Upload:**
    *   Select "Arduino Nano" in `Tools` -> `Board`.
    *   Select "ATmega328P (Old Bootloader)" if using a generic clone, or the standard one otherwise.
    *   Connect via USB and Upload.

## Future Additions
*   **WiFi Connectivity:** To add WiFi, connect an ESP8266 (e.g., NodeMCU or ESP-01) to the Arduino via Serial (RX/TX). You can modify the code to print status messages (`Serial.println("CYCLE_COMPLETE")`) which the ESP8266 can read and push to a service like Blynk or Home Assistant.
*   **Camera:** Add an ESP32-CAM module powered by the 5V rail to monitor the interior.

## Usage
1.  **Power On:** Green LED should light up.
2.  **Cat Usage:** When the cat enters, the sensor triggers. When they leave, the timer starts (Yellow LED).
3.  **Cycle:** After 7 minutes, the globe rotates to the dump position, pauses, and returns home.

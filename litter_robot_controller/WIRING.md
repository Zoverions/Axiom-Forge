# Wiring Guide: DIY Litter Robot Controller

This guide assumes you are using an **ESP32** microcontroller and an **L298N** Motor Driver. This setup replaces the original circuit board.

## Components Needed
1.  **Microcontroller:** ESP32 Development Board (NodeMCU-32S or similar).
2.  **Motor Driver:** L298N Dual H-Bridge module.
3.  **Power Supply:** 12V DC Adapter (The original Litter Robot power supply is usually 15V DC, check the label! If it is 15V, ensure your L298N supports it and DO NOT feed 15V directly to the ESP32. Use a buck converter (step-down) to 5V for the ESP32).
4.  **Sensors:**
    *   **Cat Sensor:** Reuse the original weight switch or a generic limit switch.
    *   **Position Sensors:** Reuse the original Hall Effect sensors (usually 3 wires: VCC, GND, Signal) or magnetic reed switches.

## Wiring Connections

### 1. Power Distribution
*   **12V/15V Source +** -> L298N `12V` Input
*   **12V/15V Source -** -> L298N `GND`
*   **L298N `GND`** -> ESP32 `GND` (Common Ground is critical)
*   **Buck Converter (12V/15V -> 5V)** -> ESP32 `5V` / `VIN` pin.

### 2. Motor Connection (L298N)
The Litter Robot motor has two wires.
*   **Motor Wire A** -> L298N `OUT1`
*   **Motor Wire B** -> L298N `OUT2`

### 3. Motor Control (ESP32 -> L298N)
*   **ESP32 GPIO 26** -> L298N `IN1`
*   **ESP32 GPIO 27** -> L298N `IN2`
*   **ESP32 GPIO 14** -> L298N `ENA` (PWM Speed Control - remove jumper if present)

### 4. Sensors
*   **Cat Sensor (Weight Switch):**
    *   One side to **GND**
    *   Other side to **ESP32 GPIO 33** (Code uses internal Pull-up)

*   **Home Position Sensor (Hall Effect / Magnet):**
    *   Detects when the globe is in the level "Home" position.
    *   **VCC** -> 3.3V or 5V (Check sensor spec)
    *   **GND** -> GND
    *   **Signal** -> **ESP32 GPIO 32**

*   **Dump Position Sensor (Hall Effect / Magnet):**
    *   Detects when the globe is fully rotated to dump waste.
    *   **VCC** -> 3.3V or 5V
    *   **GND** -> GND
    *   **Signal** -> **ESP32 GPIO 35**

## Summary Pinout

| ESP32 Pin | Function | Description |
| :--- | :--- | :--- |
| GPIO 26 | Motor IN1 | Direction Control A |
| GPIO 27 | Motor IN2 | Direction Control B |
| GPIO 14 | Motor PWM | Speed Control |
| GPIO 33 | Cat Sensor | Active LOW (Connect to GND when triggered) |
| GPIO 32 | Home Sensor | Active LOW (Magnetic sensor) |
| GPIO 35 | Dump Sensor | Active LOW (Magnetic sensor) |

## Important Notes
*   **Logic Levels:** The ESP32 is a 3.3V device. If you are reusing existing 5V sensors, verify they are safe for 3.3V logic or use a logic level shifter. Most open-drain hall sensors just need a pull-up to 3.3V.
*   **Motor Voltage:** Verify your motor voltage. Standard Litter Robots use ~15V. The L298N can handle this, but the ESP32 cannot.

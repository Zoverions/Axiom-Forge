# Wiring Guide: Arduino Nano Litter Robot Controller

This guide details the wiring for replacing the Litter Robot controller with an **Arduino Nano**, **L298N Motor Driver**, and **LM2596 Buck Converter**.

## Components
*   **Microcontroller:** Arduino Nano (5V Logic).
*   **Motor Driver:** L298N Dual H-Bridge Module.
*   **Power Regulation:** LM2596 DC-DC Buck Converter (Input: 15V, Output: 5V).
*   **Power Supply:** Original 15V DC Adapter.
*   **Sensors:** Original Hall Effect sensors and Cat Sensor (Switch).
*   **Passive Components:** 10kΩ Pull-up resistors (if sensors are open-collector), 10uF Capacitor (Motor noise suppression).

## Wiring Diagram

### 1. Power Distribution
The system is powered by the original 15V supply. The Motor Driver gets 15V directly, while the Arduino and sensors run on regulated 5V.

*   **15V Power Supply (+)** -> L298N `12V` Input **AND** LM2596 `IN+`
*   **15V Power Supply (-)** -> L298N `GND` **AND** LM2596 `IN-` **AND** Arduino `GND`
*   **LM2596 `OUT+` (5V)** -> Arduino `5V` (or `VIN` if stable 7-12V, but 5V pin is preferred for regulated 5V source) **AND** Sensor VCCs.
*   **LM2596 `OUT-`** -> Common Ground.

### 2. Motor Connection (L298N)
*   **L298N `OUT1`** -> Motor Wire A
*   **L298N `OUT2`** -> Motor Wire B
*   *(Optional)* Connect a 10uF capacitor across the motor terminals to reduce noise.

### 3. Logic Connections (Arduino -> L298N)
*   **Arduino D11** -> L298N `ENA` (PWM Speed Control)
*   **Arduino D12** -> L298N `IN1` (Direction A)
*   **Arduino D13** -> L298N `IN2` (Direction B)

### 4. Sensors & Inputs
*   **Cat Sensor (Weight Switch):**
    *   One side to **GND**
    *   Other side to **Arduino D4**
    *   *Note: Code uses `INPUT_PULLUP`. If false triggers occur, add external 10k resistor to 5V.*

*   **Home Position Sensor (Hall Effect):**
    *   **VCC** -> 5V
    *   **GND** -> GND
    *   **Signal** -> **Arduino D2**
    *   *Note: Code uses `INPUT_PULLUP`.*

*   **Dump Position Sensor (Hall Effect):**
    *   **VCC** -> 5V
    *   **GND** -> GND
    *   **Signal** -> **Arduino D3**
    *   *Note: Code uses `INPUT_PULLUP`.*

### 5. Optional Controls (Buttons & LEDs)
*   **Buttons (Momentary, connect to GND):**
    *   Cycle Button -> **D5**
    *   Empty Button -> **D6**
    *   Fill Button -> **D7**
*   **LEDs (Series resistor ~220Ω required):**
    *   Green (Ready) -> **D8**
    *   Yellow (Cycling) -> **D9**
    *   Red (Error) -> **D10**

### 6. Safety / Current Sense
*   **Current Sense:**
    *   If using L298N with current sense pin or ACS712 module: Connect output to **Arduino A0**.
    *   *Threshold in code is set to 800 (approx 4V on 5V scale). Adjust based on sensor.*

## Pinout Summary

| Arduino Pin | Function | Description |
| :--- | :--- | :--- |
| D2 | Home Sensor | Input (Active Low) |
| D3 | Dump Sensor | Input (Active Low) |
| D4 | Cat Sensor | Input (Active Low) |
| D5 | Btn: Cycle | Input (Active Low) |
| D6 | Btn: Empty | Input (Active Low) |
| D7 | Btn: Fill | Input (Active Low) |
| D8 | LED: Green | Output |
| D9 | LED: Yellow | Output |
| D10 | LED: Red | Output |
| D11 | Motor PWM | Output (L298N ENA) |
| D12 | Motor IN1 | Output (L298N IN1) |
| D13 | Motor IN2 | Output (L298N IN2) |
| A0 | Current Sense | Analog Input |

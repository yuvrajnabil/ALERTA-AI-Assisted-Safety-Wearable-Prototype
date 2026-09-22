# ALERTA wiring map

All GPIO assignments are centralized in `include/config.h`. Change that file
if your prototype already uses different pins.

## Signal connections

| Module | Module pin | ESP32 pin | Notes |
|---|---|---:|---|
| MPU6050 | SDA | GPIO21 | Shared I2C bus |
| MPU6050 | SCL | GPIO22 | Shared I2C bus |
| MAX30102/05 | SDA | GPIO21 | Shared I2C bus |
| MAX30102/05 | SCL | GPIO22 | Shared I2C bus |
| NEO-6M | TX | GPIO34 (RX) | Essential GPS data line |
| NEO-6M | RX | GPIO27 (TX) | Optional for most tests |
| SIM800L | TX | GPIO16 (RX2) | Cross TX to RX |
| SIM800L | RX | GPIO17 (TX2) | Check whether your board needs level shifting |
| INMP441 | SCK/BCLK | GPIO26 | I2S clock |
| INMP441 | WS/LRCL | GPIO25 | I2S word select |
| INMP441 | SD | GPIO33 | I2S data into ESP32 |
| INMP441 | L/R | GND | Selects the left channel used by the code |
| SOS button | One side | GPIO13 | Configured with internal pull-up |
| SOS button | Other side | GND | Pressing makes the input LOW |
| Active buzzer driver | Signal | GPIO18 | Use a transistor if current exceeds GPIO rating |
| Vibration driver | Signal | GPIO19 | Transistor and flyback diode required |
| Status LED | Signal | GPIO2 | Built-in LED on many ESP32 DevKit boards |

## Power connections

- Connect all **grounds** together.
- Power MPU6050, MAX30102/05 and INMP441 according to the voltage printed on
  the exact breakout board. Their signal lines must remain ESP32-compatible.
- Many NEO-6M breakouts accept 5 V at `VCC` because they contain a regulator;
  verify your own board before connecting it.
- A bare SIM800L normally needs approximately 3.7–4.2 V and can demand large
  current bursts. Use a dedicated suitable supply and a large low-ESR
  capacitor close to the modem. Never use the ESP32 3.3 V pin as its supply.
- Never power a vibration motor directly from a GPIO. Use an NPN transistor or
  logic-level MOSFET, a base/gate resistor, and a flyback diode.

## Suggested bring-up order

1. ESP32 alone.
2. MPU6050 on I2C.
3. MAX30102/05 on the same I2C bus.
4. NEO-6M outdoors.
5. INMP441.
6. Button, buzzer driver and motor driver.
7. SIM800L with its separate power supply.

Do not attach every module at once before the individual tests pass.


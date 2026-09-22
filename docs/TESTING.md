# Hardware and system test checklist

Record the date, firmware commit, wiring revision and result for every test.

## Individual hardware

- [ ] I2C scanner sees MPU6050 and MAX30102/05.
- [ ] MPU6050 values are near 1 g while stationary and change with rotation.
- [ ] MAX30102/05 reports a stable signal only when a finger is correctly placed.
- [ ] NEO-6M receives serial characters and obtains an outdoor GPS fix.
- [ ] INMP441 RMS level changes with sound without constant clipping.
- [ ] SOS button reliably reads LOW when held.
- [ ] Buzzer driver works without resetting the ESP32.
- [ ] Vibration driver works without powering the motor from the GPIO.
- [ ] SIM800L answers `AT`, reports network registration, and stays powered
      during a controlled test SMS.

## Integrated firmware

- [ ] All unavailable sensors fail gracefully instead of freezing startup.
- [ ] CSV rows have a consistent number and order of fields.
- [ ] Two-second feature values match a manually checked log segment.
- [ ] SOS requires the configured hold duration.
- [ ] GSM remains disabled during ordinary bench work.
- [ ] A test alert goes only to the project team's test number.
- [ ] GPS-unavailable messages do not contain a false coordinate.
- [ ] Health anomaly requires the configured number of consecutive windows.
- [ ] Alert outputs turn off after the configured duration.

## ML verification

- [ ] Synthetic generation is identical for the same random seed.
- [ ] Train and test participant IDs do not overlap.
- [ ] Python and generated C++ predictions are compared on shared rows.
- [ ] Results are labelled as synthetic in every report or presentation.
- [ ] Real-data evaluation is completed before any deployment claim.


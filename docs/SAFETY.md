# Safety and responsible-use notes

## Electrical safety

- The SIM800L can reset, overheat, or behave unpredictably if its supply is
  incorrect. Check the exact module specification and use a current-capable
  supply. Keep GSM transmission disabled in `config.h` during initial tests.
- The ESP32 GPIO pins cannot safely power a motor. Use a transistor/MOSFET
  driver and flyback diode.
- Confirm polarity before connecting any Li-Po battery. Use a protected cell
  and a suitable charge/protection circuit.
- Disconnect power before changing wiring.
- Test on a non-flammable surface and never leave a charging prototype
  unattended.

## Human-subject and medical safety

- The MAX30102/05 readings and the included health classifier are not a
  diagnosis.
- Never deliberately create dangerous low-oxygen, heart-rate, or fall
  conditions to collect data.
- Simulated falls should use a soft object or instrumented dummy, not a person
  falling onto a hard surface.
- Obtain informed consent and appropriate institutional/ethics approval before
  collecting identifiable or health-related human data.
- Encrypt sensitive data, collect only what is necessary, and define a deletion
  policy.
- ALERTA must supplement—not replace—caregivers, emergency services or a
  validated medical device.

## Alert safety

- Use your own phone number during tests and clearly mark messages as tests.
- Do not call emergency-service numbers while developing.
- Require persistent health anomalies and monitor false alarms.
- Provide the wearer with a way to cancel false alerts in a later hardware
  iteration.
- GPS may be unavailable indoors; the SMS explicitly reports when there is no
  valid fix.


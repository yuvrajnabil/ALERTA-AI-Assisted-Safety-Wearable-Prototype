#include <Arduino.h>

constexpr int SOS_BUTTON = 13;
constexpr int ACTIVE_BUZZER = 18;
constexpr int VIBRATION_MOTOR_DRIVER = 19;

void setAlarm(bool on) {
  digitalWrite(ACTIVE_BUZZER, on ? HIGH : LOW);
  digitalWrite(VIBRATION_MOTOR_DRIVER, on ? HIGH : LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(SOS_BUTTON, INPUT_PULLUP);
  pinMode(ACTIVE_BUZZER, OUTPUT);
  pinMode(VIBRATION_MOTOR_DRIVER, OUTPUT);
  setAlarm(false);
  Serial.println("Hold SOS button (GPIO13 to GND) to test outputs.");
  Serial.println("Drive the vibration motor through a transistor + flyback diode.");
}

void loop() {
  const bool pressed = digitalRead(SOS_BUTTON) == LOW;
  setAlarm(pressed);
  delay(10);
}

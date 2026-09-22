// Bench-safe SIM800L test. It sends nothing automatically.
// Power the modem from a suitable ~4 V supply capable of high current bursts.
// Never power a bare SIM800L from the ESP32 3.3 V pin.

#include <Arduino.h>

HardwareSerial modem(2);
const char PHONE_NUMBER[] = "+8801XXXXXXXXX";

String waitForResponse(uint32_t timeoutMs) {
  String response;
  const uint32_t start = millis();
  while (millis() - start < timeoutMs) {
    while (modem.available()) response += char(modem.read());
  }
  return response;
}

void sendSms() {
  if (String(PHONE_NUMBER).indexOf('X') >= 0) {
    Serial.println("Refusing: replace PHONE_NUMBER first.");
    return;
  }
  modem.println("AT+CMGF=1");
  Serial.println(waitForResponse(1000));
  modem.print("AT+CMGS=\"");
  modem.print(PHONE_NUMBER);
  modem.println("\"");
  Serial.println(waitForResponse(1500));
  modem.print("ALERTA bench test message");
  modem.write(26);
  Serial.println(waitForResponse(15000));
}

void setup() {
  Serial.begin(115200);
  modem.begin(9600, SERIAL_8N1, 16, 17);
  Serial.println("Commands: at | signal | network | sms");
  Serial.println("SIM800L TX->GPIO16, RX<-GPIO17, and common GND.");
}

void loop() {
  if (!Serial.available()) return;
  String command = Serial.readStringUntil('\n');
  command.trim();
  command.toLowerCase();

  if (command == "at") modem.println("AT");
  else if (command == "signal") modem.println("AT+CSQ");
  else if (command == "network") modem.println("AT+CREG?");
  else if (command == "sms") sendSms();
  else Serial.println("Unknown command.");

  if (command != "sms") Serial.println(waitForResponse(2000));
}

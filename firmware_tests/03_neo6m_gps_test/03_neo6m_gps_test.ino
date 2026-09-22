#include <TinyGPSPlus.h>

TinyGPSPlus gps;
HardwareSerial gpsSerial(1);

void setup() {
  Serial.begin(115200);
  // NEO-6M TX -> ESP32 GPIO34. NEO-6M RX -> ESP32 GPIO27 is optional.
  gpsSerial.begin(9600, SERIAL_8N1, 34, 27);
  Serial.println("Waiting for GPS. Test outdoors with a clear sky view.");
}

void loop() {
  while (gpsSerial.available()) {
    gps.encode(gpsSerial.read());
  }

  static uint32_t lastPrint = 0;
  if (millis() - lastPrint >= 1000) {
    lastPrint = millis();
    Serial.print("chars=");
    Serial.print(gps.charsProcessed());
    Serial.print(",satellites=");
    Serial.print(gps.satellites.isValid() ? String(gps.satellites.value()) : "NA");
    Serial.print(",lat=");
    Serial.print(gps.location.isValid() ? String(gps.location.lat(), 6) : "NA");
    Serial.print(",lng=");
    Serial.println(gps.location.isValid() ? String(gps.location.lng(), 6) : "NA");

    if (gps.charsProcessed() < 10 && millis() > 5000) {
      Serial.println("No GPS serial data. Recheck TX->GPIO34 and common GND.");
    }
  }
}


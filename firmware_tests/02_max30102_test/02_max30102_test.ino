#include <MAX30105.h>
#include <Wire.h>
#include <heartRate.h>
#include <spo2_algorithm.h>

MAX30105 sensor;
constexpr int BUFFER_SIZE = 100;
uint32_t redBuffer[BUFFER_SIZE];
uint32_t irBuffer[BUFFER_SIZE];
int indexInBuffer = 0;
uint32_t lastBeat = 0;

void calculateSpO2() {
  int32_t spo2 = 0;
  int8_t validSpO2 = 0;
  int32_t heartRate = 0;
  int8_t validHeartRate = 0;
  maxim_heart_rate_and_oxygen_saturation(
      irBuffer, BUFFER_SIZE, redBuffer, &spo2, &validSpO2, &heartRate,
      &validHeartRate);
  Serial.print("algorithm_hr=");
  Serial.print(validHeartRate ? String(heartRate) : "NA");
  Serial.print(",spo2=");
  Serial.println(validSpO2 ? String(spo2) : "NA");
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  Wire.setClock(400000);
  if (!sensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102/05 not found. Check 3.3V, GND, SDA=21, SCL=22.");
    while (true) delay(100);
  }
  sensor.setup(0x1F, 4, 2, 100, 411, 4096);
  sensor.setPulseAmplitudeGreen(0);
  Serial.println("Place a finger steadily on the sensor.");
}

void loop() {
  sensor.check();
  while (sensor.available()) {
    const uint32_t red = sensor.getFIFORed();
    const uint32_t ir = sensor.getFIFOIR();
    sensor.nextSample();

    if (ir > 5000 && checkForBeat(ir)) {
      const uint32_t now = millis();
      const uint32_t delta = now - lastBeat;
      lastBeat = now;
      if (delta > 250 && delta < 2000) {
        Serial.print("beat_bpm=");
        Serial.println(60000.0F / delta, 1);
      }
    }

    redBuffer[indexInBuffer] = red;
    irBuffer[indexInBuffer] = ir;
    ++indexInBuffer;
    if (indexInBuffer == BUFFER_SIZE) {
      calculateSpO2();
      indexInBuffer = 0;
    }
  }
}


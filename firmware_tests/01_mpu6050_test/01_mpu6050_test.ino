#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("MPU6050 not found. Check 3.3V, GND, SDA=21, SCL=22.");
    while (true) delay(100);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_44_HZ);
  Serial.println("ax_g,ay_g,az_g,accel_magnitude_g,gyro_magnitude_dps");
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  const float ax = a.acceleration.x / 9.80665F;
  const float ay = a.acceleration.y / 9.80665F;
  const float az = a.acceleration.z / 9.80665F;
  const float acceleration = sqrtf(ax * ax + ay * ay + az * az);
  const float gx = g.gyro.x * 57.2957795F;
  const float gy = g.gyro.y * 57.2957795F;
  const float gz = g.gyro.z * 57.2957795F;
  const float rotation = sqrtf(gx * gx + gy * gy + gz * gz);

  Serial.printf("%.3f,%.3f,%.3f,%.3f,%.1f\n", ax, ay, az, acceleration,
                rotation);
  delay(20);  // 50 Hz
}


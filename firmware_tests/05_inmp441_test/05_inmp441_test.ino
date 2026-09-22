#include <driver/i2s.h>

constexpr i2s_port_t PORT = I2S_NUM_0;

void setup() {
  Serial.begin(115200);

  i2s_config_t cfg{};
  cfg.mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX);
  cfg.sample_rate = 16000;
  cfg.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
  cfg.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
  cfg.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  cfg.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  cfg.dma_buf_count = 4;
  cfg.dma_buf_len = 256;

  i2s_pin_config_t pins{};
  pins.bck_io_num = 26;
  pins.ws_io_num = 25;
  pins.data_out_num = I2S_PIN_NO_CHANGE;
  pins.data_in_num = 33;

  if (i2s_driver_install(PORT, &cfg, 0, nullptr) != ESP_OK ||
      i2s_set_pin(PORT, &pins) != ESP_OK) {
    Serial.println("I2S setup failed.");
    while (true) delay(100);
  }
  Serial.println("INMP441: SCK=26, WS=25, SD=33, L/R=GND (left channel)");
  Serial.println("rms,dbfs");
}

void loop() {
  int32_t samples[256];
  size_t bytesRead = 0;
  if (i2s_read(PORT, samples, sizeof(samples), &bytesRead,
               pdMS_TO_TICKS(200)) != ESP_OK || bytesRead == 0) {
    return;
  }

  const size_t count = bytesRead / sizeof(int32_t);
  double sumSquares = 0.0;
  for (size_t i = 0; i < count; ++i) {
    const float normalized = float(samples[i] >> 8) / 8388608.0F;
    sumSquares += double(normalized) * normalized;
  }
  const float rms = sqrtf(float(sumSquares / count));
  const float dbfs = 20.0F * log10f(rms + 1.0e-9F);
  Serial.printf("%.6f,%.1f\n", rms, dbfs);
}


#include <cmath>
#include <iostream>

#include "generated_models.h"

int main() {
  const float fall[alerta_model::FALL_FEATURE_COUNT] = {
      1.08F, 0.51F, 3.80F, 390.0F, 72.0F, 1.10F};
  const float health[alerta_model::HEALTH_FEATURE_COUNT] = {
      138.0F, 87.0F, 0.72F, 1.08F, 0.51F};
  const float fall_probability =
      alerta_model::predict_fall_probability(fall);
  const float health_probability =
      alerta_model::predict_health_probability(health);
  std::cout << fall_probability << "," << health_probability << "\n";
  if (!std::isfinite(fall_probability) || fall_probability < 0.0F ||
      fall_probability > 1.0F) {
    return 1;
  }
  if (!std::isfinite(health_probability) || health_probability < 0.0F ||
      health_probability > 1.0F) {
    return 2;
  }
  return 0;
}


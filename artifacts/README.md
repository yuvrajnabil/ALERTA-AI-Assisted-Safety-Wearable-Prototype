# Model artifacts

Run `ml/train_models.py` to create:

- `fall_model.joblib` and `health_model.joblib` for desktop Python;
- per-task test predictions and feature importance tables;
- confusion-matrix images;
- `metrics.json` with the seed and grouped synthetic evaluation;
- `include/generated_models.h` for ESP32 inference.

The `.joblib` files are excluded from Git by default because binary model files
can be regenerated from the versioned data and scripts.


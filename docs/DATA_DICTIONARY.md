# Synthetic dataset dictionary

Each row represents one simulated two-second feature window.

| Column | Unit/type | Meaning |
|---|---|---|
| `sample_id` | string | Unique synthetic window ID |
| `subject_id` | string | Synthetic profile used for grouped splitting |
| `scenario` | category | Generator scenario; excluded from model features |
| `accel_mean_g` | g | Mean acceleration-vector magnitude |
| `accel_std_g` | g | Standard deviation of acceleration magnitude |
| `accel_peak_g` | g | Maximum acceleration magnitude |
| `gyro_peak_dps` | degrees/s | Maximum angular-speed magnitude |
| `posture_change_deg` | degrees | Absolute start-to-end pitch change |
| `immobility_s` | seconds | Low-motion duration at the end of the window |
| `heart_rate_bpm` | bpm | Simulated pulse rate; may be missing |
| `spo2_percent` | percent | Simulated oxygen saturation; may be missing |
| `ppg_signal_quality` | 0–1 | Simplified contact/motion quality score |
| `label_fall` | 0/1 | Synthetic fall target |
| `label_health_anomaly` | 0/1 | Synthetic unusual-health-window target |

The `scenario` column is metadata and must not be used as a training feature,
because it directly encodes how the row was generated.


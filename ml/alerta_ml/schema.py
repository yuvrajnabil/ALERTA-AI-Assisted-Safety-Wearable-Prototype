"""Single source of truth for model feature order."""

FALL_FEATURES = [
    "accel_mean_g",
    "accel_std_g",
    "accel_peak_g",
    "gyro_peak_dps",
    "posture_change_deg",
    "immobility_s",
]

HEALTH_FEATURES = [
    "heart_rate_bpm",
    "spo2_percent",
    "ppg_signal_quality",
    "accel_mean_g",
    "accel_std_g",
]

METADATA_COLUMNS = ["sample_id", "subject_id", "scenario"]
TARGET_COLUMNS = ["label_fall", "label_health_anomaly"]
REQUIRED_COLUMNS = METADATA_COLUMNS + sorted(
    set(FALL_FEATURES + HEALTH_FEATURES)
) + TARGET_COLUMNS


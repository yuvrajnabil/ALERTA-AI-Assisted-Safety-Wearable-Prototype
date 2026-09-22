#!/usr/bin/env python3
"""Capture labelled ALERTA firmware windows from an ESP32 serial port.

Only run a human-data collection protocol after consent and appropriate ethics
review. This script does not anonymize or encrypt its output.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import serial


FIRMWARE_COLUMNS = [
    "timestamp_ms",
    "accel_magnitude_g",
    "gyro_magnitude_dps",
    "heart_rate_bpm",
    "spo2_percent",
    "ppg_signal_quality",
    "sound_dbfs",
    "latitude",
    "longitude",
    "accel_mean_g",
    "accel_std_g",
    "accel_peak_g",
    "gyro_peak_dps",
    "posture_change_deg",
    "immobility_s",
    "fall_probability",
    "health_probability",
    "alert_reason",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True, help="Example: /dev/cu.usbserial-0001")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--subject-id", required=True, help="Use a coded, non-name ID")
    parser.add_argument("--scenario", required=True, help="Example: walk or safe_fall_dummy")
    parser.add_argument("--label-fall", type=int, choices=[0, 1], required=True)
    parser.add_argument("--label-health", type=int, choices=[0, 1], required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    new_file = not args.output.exists() or args.output.stat().st_size == 0

    print("Press Ctrl+C to stop. Comment/status lines beginning with # are ignored.")
    with serial.Serial(args.port, args.baud, timeout=2) as device, args.output.open(
        "a", newline="", encoding="utf-8"
    ) as output:
        columns = ["sample_id", "subject_id", "scenario"] + FIRMWARE_COLUMNS + [
            "label_fall",
            "label_health_anomaly",
        ]
        writer = csv.writer(output)
        if new_file:
            writer.writerow(columns)

        try:
            while True:
                line = device.readline().decode("utf-8", errors="replace").strip()
                if not line or line.startswith("#") or line.startswith("timestamp_ms"):
                    continue
                values = next(csv.reader([line]))
                if len(values) != len(FIRMWARE_COLUMNS):
                    print(f"Skipped malformed row with {len(values)} fields")
                    continue
                sample_id = f"{args.subject_id}-{args.scenario}-{values[0]}"
                writer.writerow(
                    [sample_id, args.subject_id, args.scenario]
                    + values
                    + [args.label_fall, args.label_health]
                )
                output.flush()
                print(line)
        except KeyboardInterrupt:
            print(f"\nSaved capture to {args.output}")


if __name__ == "__main__":
    main()

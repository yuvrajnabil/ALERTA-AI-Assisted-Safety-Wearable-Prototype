# Model card: ALERTA simulation baselines

## Intended use

Two small Random Forest classifiers demonstrate an end-to-end embedded ML
pipeline:

1. `fall`: screens a two-second motion-feature window for a possible fall.
2. `health`: screens pulse-oximetry and motion features for an unusual window.

They are intended for software integration, feature-order verification and
initial firmware testing.

## Not intended for

- clinical diagnosis, triage or treatment;
- autonomous emergency decisions without confirmation;
- reporting medical accuracy or real-world safety performance;
- deployment to vulnerable users before ethics, usability and field testing.

## Training data

`data/alerta_synthetic_v1.csv` contains generated subject profiles and
two-second feature windows. It contains no real patient data. Distributions
overlap and include missing PPG values and small label noise, but they remain a
simplification of real sensor behavior.

## Features

### Fall model

- acceleration mean, standard deviation and peak in g;
- peak gyroscope magnitude in degrees/second;
- pitch/posture change in degrees;
- terminal immobility duration in seconds.

### Health model

- heart rate in beats/minute;
- SpO2 percentage;
- PPG signal-quality proxy;
- acceleration mean and standard deviation.

## Evaluation design

The script separates synthetic `subject_id` groups between train and test
sets. A second grouped validation split selects a decision threshold with a
recall target. The final forest is refitted on all non-test subjects and is
evaluated once on the held-out synthetic subjects.

Reported metrics include accuracy, balanced accuracy, precision, recall, F1,
ROC-AUC and the confusion matrix. Because every record is synthetic, even high
scores are **pipeline checks**, not evidence of real performance.

## Embedded export

The exporter converts each fitted decision tree to ordinary nested C++
conditions and averages leaf probabilities. Missing values are replaced using
training-set medians in both desktop and embedded inference. The feature order
in `ml/alerta_ml/schema.py` matches `src/main.cpp`.

## Required next validation

- compare embedded and Python predictions on identical real feature rows;
- collect labelled activities of daily living and safe fall simulations;
- measure performance by unseen participant and device placement;
- measure false alarms per hour/day and time-to-alert;
- compare heart rate and SpO2 with an appropriate reference device;
- assess demographic, skin-contact, motion and environment effects;
- calibrate thresholds without using the final test participants.


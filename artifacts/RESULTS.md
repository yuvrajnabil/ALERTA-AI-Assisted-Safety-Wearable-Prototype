# Reproducible simulation results

Generated with 6,000 synthetic two-second windows, 80 synthetic subjects and
random seed 42. Sixteen synthetic subjects were held out from each final test
set.

| Task | Threshold | Accuracy | Balanced accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fall screening | 0.85 | 0.9868 | 0.9398 | 0.9811 | 0.8814 | 0.9286 | 0.9685 |
| Health-anomaly screening | 0.46 | 0.9711 | 0.8945 | 0.8046 | 0.8046 | 0.8046 | 0.9157 |

Fall confusion matrix (`negative`, `positive`):

```text
[[1091,  2],
 [  14,104]]
```

Health-anomaly confusion matrix (`negative`, `positive`):

```text
[[1074,17],
 [  17,70]]
```

These results verify that the software pipeline, grouped split, saved Python
models and generated C++ inference work together. They **must not** be quoted as
clinical accuracy or real-world validation. See `docs/MODEL_CARD.md` for the
required next evaluation.


# RA-PatchTST results, ETTh1, lookback 336, horizon 96

Seeds per variant: A0: 2, A1: 2, A2: 2, A3: 2, A4: 2. Cells are mean ± std over seeds (std shown only when ≥2 seeds). Test MSE in scaled units; lower is better.

## 1. Clean-data reproduction (checkpoint chosen on clean validation loss)

| Model | Test MSE | Test MAE | Paper MSE / MAE |
|---|---|---|---|
| A0 PatchTST (baseline) | 0.379 ± 0.001 | 0.401 ± 0.001 | 0.375 / 0.399 |
| A1 + corruption training | 0.382 ± 0.001 | 0.405 ± 0.001 | 0.375 / 0.399 |

## 2. Test MSE by corruption type (mean over the levels in each group)

| Model | clean | missing (point) | missing (16-stretch) | noise | anomaly | shift | mixed | avg of 21 corruptions |
|---|---|---|---|---|---|---|---|---|
| A0 PatchTST (baseline) | 0.379 ± 0.001 | 0.387 ± 0.001 | 0.392 ± 0.001 | 0.384 ± 0.001 | 0.458 ± 0.005 | 0.520 ± 0.006 | 0.452 ± 0.004 | 0.429 ± 0.001 |
| A1 + corruption training | 0.382 ± 0.001 | 0.391 ± 0.001 | 0.395 ± 0.001 | 0.386 ± 0.001 | 0.431 ± 0.004 | 0.477 ± 0.001 | 0.431 ± 0.003 | 0.417 ± 0.001 |
| A2 A1 + shift head | 0.382 ± 0.000 | 0.392 ± 0.001 | 0.396 ± 0.001 | 0.385 ± 0.000 | 0.431 ± 0.004 | 0.466 ± 0.002 | 0.431 ± 0.003 | 0.415 ± 0.001 |
| A3 A1 + reliability gate | 0.383 ± 0.001 | 0.391 ± 0.002 | 0.395 ± 0.001 | 0.386 ± 0.001 | 0.430 ± 0.002 | 0.472 ± 0.004 | 0.429 ± 0.001 | 0.416 ± 0.000 |
| A4 full RA-PatchTST | 0.382 ± 0.000 | 0.392 ± 0.001 | 0.396 ± 0.001 | 0.385 ± 0.000 | 0.429 ± 0.002 | 0.462 ± 0.003 | 0.429 ± 0.001 | 0.413 ± 0.000 |

## 3a. Change in MSE versus A0 PatchTST (baseline) (negative = better)

| Model | clean | missing (point) | missing (16-stretch) | noise | anomaly | shift | mixed | avg of 21 corruptions |
|---|---|---|---|---|---|---|---|---|
| A1 + corruption training | +0.9% | +1.0% | +0.7% | +0.4% | -5.8% | -8.3% | -4.7% | -3.0% |
| A2 A1 + shift head | +0.7% | +1.2% | +0.9% | +0.2% | -6.0% | -10.3% | -4.7% | -3.4% |
| A3 A1 + reliability gate | +1.0% | +1.1% | +0.8% | +0.5% | -6.3% | -9.1% | -5.1% | -3.2% |
| A4 full RA-PatchTST | +0.7% | +1.3% | +0.9% | +0.2% | -6.5% | -11.0% | -5.2% | -3.7% |

## 3b. Change in MSE versus A1 + corruption training (negative = better)

| Model | clean | missing (point) | missing (16-stretch) | noise | anomaly | shift | mixed | avg of 21 corruptions |
|---|---|---|---|---|---|---|---|---|
| A0 PatchTST (baseline) | -0.9% | -1.0% | -0.7% | -0.4% | +6.2% | +9.0% | +4.9% | +3.1% |
| A2 A1 + shift head | -0.2% | +0.2% | +0.2% | -0.2% | -0.2% | -2.2% | -0.0% | -0.5% |
| A3 A1 + reliability gate | +0.1% | +0.1% | +0.1% | +0.1% | -0.4% | -0.9% | -0.4% | -0.3% |
| A4 full RA-PatchTST | -0.2% | +0.2% | +0.2% | -0.2% | -0.7% | -3.0% | -0.5% | -0.8% |

## 4. Paired per-seed comparison against A1 (average of the 21 corruption settings)

| Model | Seeds | Mean ΔMSE vs A1 | Seeds better than A1 | Per-seed ΔMSE |
|---|---|---|---|---|
| A2 A1 + shift head | 2 | -0.0020 | 2/2 | -0.0016, -0.0023 |
| A3 A1 + reliability gate | 2 | -0.0011 | 2/2 | -0.0004, -0.0018 |
| A4 full RA-PatchTST | 2 | -0.0032 | 2/2 | -0.0025, -0.0039 |

## 5. Cost

| Model | Parameters | of which gate | Train s/epoch (1 CPU thread) | Inference s, 2,785 test windows | Epochs run |
|---|---|---|---|---|---|
| A0 PatchTST (baseline) | 81,728 | 0 | 37.0 | 5.14 | 20.0 |
| A1 + corruption training | 81,728 | 0 | 39.0 | 4.31 | 20.0 |
| A2 A1 + shift head | 81,920 | 0 | 39.9 | 4.17 | 20.0 |
| A3 A1 + reliability gate | 82,529 | 801 | 41.0 | 5.49 | 20.0 |
| A4 full RA-PatchTST | 82,721 | 801 | 41.2 | 5.13 | 20.0 |

## 6. Does the gate do what it should? Mean gate weight on corrupted vs clean patches

A patch counts as corrupted if any of its 16 values was altered. 1.0 = fully trusted, 0 = ignored.

| Model | Setting | Share of patches corrupted | Gate on corrupted | Gate on clean |
|---|---|---|---|---|
| A3 A1 + reliability gate | clean | 0.00 | - | 0.956 |
| A3 A1 + reliability gate | missing_5 | 0.55 | 0.953 | 0.957 |
| A3 A1 + reliability gate | missingpatch_5 | 0.09 | 0.954 | 0.956 |
| A3 A1 + reliability gate | noise_5 | 0.55 | 0.949 | 0.958 |
| A3 A1 + reliability gate | anomaly_5 | 0.55 | 0.926 | 0.963 |
| A3 A1 + reliability gate | shift_3 | 0.37 | 0.944 | 0.962 |
| A3 A1 + reliability gate | mixed | 0.92 | 0.941 | 0.963 |
| A4 full RA-PatchTST | clean | 0.00 | - | 0.958 |
| A4 full RA-PatchTST | missing_5 | 0.55 | 0.957 | 0.959 |
| A4 full RA-PatchTST | missingpatch_5 | 0.09 | 0.955 | 0.959 |
| A4 full RA-PatchTST | noise_5 | 0.55 | 0.954 | 0.960 |
| A4 full RA-PatchTST | anomaly_5 | 0.55 | 0.939 | 0.964 |
| A4 full RA-PatchTST | shift_3 | 0.37 | 0.946 | 0.963 |
| A4 full RA-PatchTST | mixed | 0.92 | 0.949 | 0.964 |

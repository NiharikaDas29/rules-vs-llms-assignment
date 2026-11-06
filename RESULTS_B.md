# Project B results

## Dataset status

The specified 2023 NYC 311 dataset was not present in the repository or local
workspace. Consequently, this document reports only a controlled synthetic
batch, not NYC 311 real-data quality findings.

## Controlled experiment

The injector was run on a four-row fixture containing common NYC 311 columns.
It produced six rows after exact and near-duplicate additions and labelled the
injected corruption types. The run measured rule, statistical, local semantic,
and hybrid detectors using actual `perf_counter()` timings.

One executed batch produced these aggregate values:

| Detector | Recall | False-positive rate | Time (seconds) |
|---|---:|---:|---:|
| Rules | 1.0 | 1.0 | 0.026136 |
| Statistics | 0.0 | 0.0 | 0.008294 |
| Local semantic baseline | 0.0 | 0.0 | 0.011350 |
| Hybrid | 1.0 | 1.0 | 0.036963 |

Measured throughput for this six-row fixture was 229.57 rows/second for
rules, 723.38 for statistics, 528.65 for the local semantic baseline, and
162.32 for hybrid. These values are too small and synthetic to extrapolate to
the NYC dataset.

These are synthetic fixture measurements only. The aggregate false-positive
rate is sensitive to the fact that a detector may flag a row for a different
corruption than the one being scored; the executable experiment now also
writes `by_type` recall and false-positive metrics for each label.

No throughput extrapolation, cost per million rows, real-data metric, or Gemini
metric is claimed. Gemini execution requires an external API call and a defined
batch/cost protocol.

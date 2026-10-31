# Simulated-pair evaluation

All after images are simulated repairs or deliberately mismatched/reused evidence. This measures synthetic consistency, not real-world repair accuracy.

Thresholds were tuned on these simulated pairs; this is not an independent held-out evaluation.

Mask mode: `auto`. Marked ROIs are supplied; optional YOLO suggestions are not required.
Planned: 120; completed: 120; errors: 0; unattempted: 0.

Accuracy on completed pairs: 120/120 (100.0%).
Average verification time: 302.0 ms.

| Expected / predicted | FIXED | PARTIAL | NOT_FIXED | SUSPICIOUS | NEEDS_REVIEW |
|---|---:|---:|---:|---:|---:|
| FIXED | 24 | 0 | 0 | 0 | 0 |
| PARTIAL | 0 | 24 | 0 | 0 | 0 |
| NOT_FIXED | 0 | 0 | 24 | 0 | 0 |
| SUSPICIOUS | 0 | 0 | 0 | 48 | 0 |
| NEEDS_REVIEW | 0 | 0 | 0 | 0 | 0 |

| Photo | Type | Seed | Expected | Actual / error | Mask | ms |
|---|---|---:|---|---|---|---:|
| pothole_1.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 366.9 |
| pothole_1.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 157.6 |
| pothole_1.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 156.7 |
| pothole_1.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 154.6 |
| pothole_1.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 156.3 |
| pothole_1.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 160.8 |
| pothole_1.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 158.4 |
| pothole_1.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 162.2 |
| pothole_1.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 154.9 |
| pothole_1.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 93.9 |
| pothole_1.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 92.9 |
| pothole_1.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 100.2 |
| pothole_1.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 152.3 |
| pothole_1.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 154.1 |
| pothole_1.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 153.4 |
| pothole_2.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 356.3 |
| pothole_2.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 345.6 |
| pothole_2.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 350.4 |
| pothole_2.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 347.6 |
| pothole_2.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 343.5 |
| pothole_2.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 348.5 |
| pothole_2.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 347.6 |
| pothole_2.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 345.0 |
| pothole_2.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 344.7 |
| pothole_2.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 98.9 |
| pothole_2.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 102.6 |
| pothole_2.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 105.8 |
| pothole_2.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 347.3 |
| pothole_2.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 351.0 |
| pothole_2.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 348.7 |
| pothole_4.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 667.5 |
| pothole_4.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 655.6 |
| pothole_4.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 656.9 |
| pothole_4.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 662.4 |
| pothole_4.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 659.9 |
| pothole_4.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 662.8 |
| pothole_4.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 665.7 |
| pothole_4.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 666.5 |
| pothole_4.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 663.3 |
| pothole_4.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 92.9 |
| pothole_4.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 128.6 |
| pothole_4.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 108.6 |
| pothole_4.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 666.8 |
| pothole_4.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 656.0 |
| pothole_4.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 661.4 |
| pothole_5.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 249.7 |
| pothole_5.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 252.7 |
| pothole_5.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 255.3 |
| pothole_5.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 255.7 |
| pothole_5.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 298.0 |
| pothole_5.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 284.7 |
| pothole_5.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 267.9 |
| pothole_5.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 258.2 |
| pothole_5.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 257.6 |
| pothole_5.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 100.3 |
| pothole_5.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 101.8 |
| pothole_5.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 104.8 |
| pothole_5.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 252.5 |
| pothole_5.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 274.5 |
| pothole_5.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 254.6 |
| pothole_6.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 233.1 |
| pothole_6.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 232.9 |
| pothole_6.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 234.2 |
| pothole_6.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 234.0 |
| pothole_6.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 231.2 |
| pothole_6.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 232.0 |
| pothole_6.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 231.5 |
| pothole_6.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 230.0 |
| pothole_6.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 230.3 |
| pothole_6.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 92.4 |
| pothole_6.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 96.0 |
| pothole_6.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 93.9 |
| pothole_6.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 228.8 |
| pothole_6.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 230.2 |
| pothole_6.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 229.2 |
| pothole_7.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 349.2 |
| pothole_7.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 353.2 |
| pothole_7.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 351.3 |
| pothole_7.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 357.7 |
| pothole_7.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 353.0 |
| pothole_7.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 353.7 |
| pothole_7.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 414.5 |
| pothole_7.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 354.9 |
| pothole_7.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 351.5 |
| pothole_7.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 103.8 |
| pothole_7.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 108.5 |
| pothole_7.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 107.5 |
| pothole_7.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 352.5 |
| pothole_7.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 351.4 |
| pothole_7.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 352.1 |
| pothole_9.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 540.9 |
| pothole_9.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 541.6 |
| pothole_9.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 539.2 |
| pothole_9.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 540.7 |
| pothole_9.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 539.1 |
| pothole_9.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 535.0 |
| pothole_9.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 535.4 |
| pothole_9.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 537.3 |
| pothole_9.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 539.9 |
| pothole_9.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 93.1 |
| pothole_9.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 96.3 |
| pothole_9.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 95.2 |
| pothole_9.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 538.3 |
| pothole_9.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 542.6 |
| pothole_9.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 542.5 |
| pothole_10.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 239.4 |
| pothole_10.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 240.7 |
| pothole_10.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 238.7 |
| pothole_10.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 239.6 |
| pothole_10.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 244.2 |
| pothole_10.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 241.1 |
| pothole_10.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 243.3 |
| pothole_10.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 246.8 |
| pothole_10.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 244.7 |
| pothole_10.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 95.1 |
| pothole_10.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 97.5 |
| pothole_10.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 100.5 |
| pothole_10.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 242.8 |
| pothole_10.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 243.0 |
| pothole_10.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 245.2 |

Each pair is evaluated independently. Duplicate cases register the identical after image under a different complaint ID; no other test hashes contaminate repair scores.
Three deterministic jitter seeds are used for every photo/type. Wrong-location pairs use another road photo and GPS approximately 140 m away.

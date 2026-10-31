# Simulated-pair evaluation

All after images are simulated repairs or deliberately mismatched/reused evidence. This measures synthetic consistency, not real-world repair accuracy.

Mask mode: `auto`. Marked ROIs are supplied; optional YOLO suggestions are not required.
Planned: 120; completed: 120; errors: 0; unattempted: 0.

Accuracy on completed pairs: 111/120 (92.5%).
Average verification time: 293.3 ms.

| Expected / predicted | FIXED | PARTIAL | NOT_FIXED | SUSPICIOUS | NEEDS_REVIEW |
|---|---:|---:|---:|---:|---:|
| FIXED | 21 | 0 | 0 | 0 | 3 |
| PARTIAL | 0 | 21 | 0 | 0 | 3 |
| NOT_FIXED | 0 | 0 | 21 | 0 | 3 |
| SUSPICIOUS | 0 | 0 | 0 | 48 | 0 |
| NEEDS_REVIEW | 0 | 0 | 0 | 0 | 0 |

| Photo | Type | Seed | Expected | Actual / error | Mask | ms |
|---|---|---:|---|---|---|---:|
| pothole_1.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 356.3 |
| pothole_1.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 140.5 |
| pothole_1.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 147.8 |
| pothole_1.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 145.6 |
| pothole_1.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 248.5 |
| pothole_1.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 146.3 |
| pothole_1.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 143.1 |
| pothole_1.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 141.1 |
| pothole_1.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 140.1 |
| pothole_1.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 94.3 |
| pothole_1.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 103.0 |
| pothole_1.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 110.2 |
| pothole_1.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 139.1 |
| pothole_1.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 140.4 |
| pothole_1.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 143.7 |
| pothole_2.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 348.5 |
| pothole_2.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 337.7 |
| pothole_2.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 336.0 |
| pothole_2.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 340.5 |
| pothole_2.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 334.2 |
| pothole_2.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 336.0 |
| pothole_2.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 340.7 |
| pothole_2.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 335.7 |
| pothole_2.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 333.6 |
| pothole_2.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 100.9 |
| pothole_2.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 105.1 |
| pothole_2.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 103.6 |
| pothole_2.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 336.2 |
| pothole_2.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 334.3 |
| pothole_2.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 335.7 |
| pothole_4.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 647.2 |
| pothole_4.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 657.8 |
| pothole_4.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 758.2 |
| pothole_4.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 651.8 |
| pothole_4.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 652.4 |
| pothole_4.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 642.3 |
| pothole_4.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 694.9 |
| pothole_4.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 678.4 |
| pothole_4.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 655.4 |
| pothole_4.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 92.5 |
| pothole_4.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 96.7 |
| pothole_4.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 96.2 |
| pothole_4.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 657.4 |
| pothole_4.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 640.6 |
| pothole_4.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 634.5 |
| pothole_5.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 235.1 |
| pothole_5.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 235.9 |
| pothole_5.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 237.0 |
| pothole_5.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 240.2 |
| pothole_5.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 234.2 |
| pothole_5.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 233.3 |
| pothole_5.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 232.8 |
| pothole_5.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 234.6 |
| pothole_5.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 233.5 |
| pothole_5.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 99.5 |
| pothole_5.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 102.1 |
| pothole_5.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 102.7 |
| pothole_5.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 237.9 |
| pothole_5.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 235.9 |
| pothole_5.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 236.2 |
| pothole_6.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 216.5 |
| pothole_6.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 217.4 |
| pothole_6.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 219.6 |
| pothole_6.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 217.2 |
| pothole_6.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 216.1 |
| pothole_6.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 216.5 |
| pothole_6.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 216.7 |
| pothole_6.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 223.6 |
| pothole_6.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 220.1 |
| pothole_6.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 96.3 |
| pothole_6.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 99.0 |
| pothole_6.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 95.7 |
| pothole_6.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 216.2 |
| pothole_6.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 217.9 |
| pothole_6.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 215.7 |
| pothole_7.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 331.2 |
| pothole_7.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 331.6 |
| pothole_7.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 332.7 |
| pothole_7.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 332.1 |
| pothole_7.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 339.6 |
| pothole_7.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 335.4 |
| pothole_7.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 332.0 |
| pothole_7.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 328.9 |
| pothole_7.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 331.2 |
| pothole_7.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 101.7 |
| pothole_7.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 104.2 |
| pothole_7.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 103.9 |
| pothole_7.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 331.0 |
| pothole_7.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 327.3 |
| pothole_7.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 330.9 |
| pothole_9.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 527.0 |
| pothole_9.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 525.0 |
| pothole_9.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 527.4 |
| pothole_9.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 539.0 |
| pothole_9.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 535.3 |
| pothole_9.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 527.6 |
| pothole_9.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 523.9 |
| pothole_9.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 531.2 |
| pothole_9.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 526.3 |
| pothole_9.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 95.9 |
| pothole_9.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 96.8 |
| pothole_9.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 98.5 |
| pothole_9.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 532.5 |
| pothole_9.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 526.5 |
| pothole_9.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 524.8 |
| pothole_10.jpg | fixed | 0 | FIXED | NEEDS_REVIEW | ellipse_fallback | 231.2 |
| pothole_10.jpg | fixed | 1 | FIXED | NEEDS_REVIEW | ellipse_fallback | 231.3 |
| pothole_10.jpg | fixed | 2 | FIXED | NEEDS_REVIEW | ellipse_fallback | 233.8 |
| pothole_10.jpg | partial | 0 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 232.4 |
| pothole_10.jpg | partial | 1 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 231.8 |
| pothole_10.jpg | partial | 2 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 231.8 |
| pothole_10.jpg | not_fixed | 0 | NOT_FIXED | NEEDS_REVIEW | none | 234.5 |
| pothole_10.jpg | not_fixed | 1 | NOT_FIXED | NEEDS_REVIEW | none | 236.7 |
| pothole_10.jpg | not_fixed | 2 | NOT_FIXED | NEEDS_REVIEW | none | 274.0 |
| pothole_10.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 108.6 |
| pothole_10.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 147.3 |
| pothole_10.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 107.7 |
| pothole_10.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 247.9 |
| pothole_10.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 264.7 |
| pothole_10.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 256.6 |

Each pair is evaluated independently. Duplicate cases register the identical after image under a different complaint ID; no other test hashes contaminate repair scores.
Three deterministic jitter seeds are used for every photo/type. Wrong-location pairs use another road photo and GPS approximately 140 m away.

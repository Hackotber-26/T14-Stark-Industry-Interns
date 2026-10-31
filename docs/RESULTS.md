# Simulated-pair evaluation

All after images are simulated repairs or deliberately mismatched/reused evidence. This measures synthetic consistency, not real-world repair accuracy.

Mask mode: `auto`. Marked ROIs are supplied; optional YOLO suggestions are not required.
Planned: 120; completed: 120; errors: 0; unattempted: 0.

Accuracy on completed pairs: 102/120 (85.0%).
Average verification time: 277.1 ms.

| Expected / predicted | FIXED | PARTIAL | NOT_FIXED | SUSPICIOUS | NEEDS_REVIEW |
|---|---:|---:|---:|---:|---:|
| FIXED | 18 | 0 | 0 | 0 | 6 |
| PARTIAL | 0 | 18 | 0 | 0 | 6 |
| NOT_FIXED | 0 | 0 | 18 | 0 | 6 |
| SUSPICIOUS | 0 | 0 | 0 | 48 | 0 |
| NEEDS_REVIEW | 0 | 0 | 0 | 0 | 0 |

| Photo | Type | Seed | Expected | Actual / error | Mask | ms |
|---|---|---:|---|---|---|---:|
| pothole_1.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 317.4 |
| pothole_1.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 138.1 |
| pothole_1.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 135.6 |
| pothole_1.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 138.7 |
| pothole_1.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 137.9 |
| pothole_1.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 140.8 |
| pothole_1.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 140.0 |
| pothole_1.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 137.5 |
| pothole_1.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 135.9 |
| pothole_1.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 95.8 |
| pothole_1.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 96.9 |
| pothole_1.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 93.0 |
| pothole_1.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 146.0 |
| pothole_1.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 137.6 |
| pothole_1.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 137.4 |
| pothole_2.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 329.5 |
| pothole_2.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 316.7 |
| pothole_2.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 333.0 |
| pothole_2.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 310.5 |
| pothole_2.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 343.8 |
| pothole_2.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 319.0 |
| pothole_2.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 317.3 |
| pothole_2.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 313.7 |
| pothole_2.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 313.8 |
| pothole_2.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 100.0 |
| pothole_2.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 100.8 |
| pothole_2.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 100.6 |
| pothole_2.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 318.7 |
| pothole_2.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 312.4 |
| pothole_2.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 330.4 |
| pothole_4.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 606.7 |
| pothole_4.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 606.2 |
| pothole_4.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 612.2 |
| pothole_4.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 652.9 |
| pothole_4.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 618.6 |
| pothole_4.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 655.1 |
| pothole_4.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 627.3 |
| pothole_4.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 551.2 |
| pothole_4.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 605.8 |
| pothole_4.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 90.6 |
| pothole_4.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 93.8 |
| pothole_4.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 95.4 |
| pothole_4.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 625.7 |
| pothole_4.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 557.7 |
| pothole_4.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 669.3 |
| pothole_5.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 233.2 |
| pothole_5.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 234.4 |
| pothole_5.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 233.2 |
| pothole_5.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 233.8 |
| pothole_5.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 233.9 |
| pothole_5.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 234.7 |
| pothole_5.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 234.3 |
| pothole_5.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 233.6 |
| pothole_5.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 240.1 |
| pothole_5.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 100.6 |
| pothole_5.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 102.0 |
| pothole_5.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 101.5 |
| pothole_5.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 232.8 |
| pothole_5.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 231.5 |
| pothole_5.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 236.4 |
| pothole_6.jpg | fixed | 0 | FIXED | NEEDS_REVIEW | ellipse_fallback | 166.1 |
| pothole_6.jpg | fixed | 1 | FIXED | NEEDS_REVIEW | ellipse_fallback | 173.6 |
| pothole_6.jpg | fixed | 2 | FIXED | NEEDS_REVIEW | ellipse_fallback | 185.1 |
| pothole_6.jpg | partial | 0 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 170.6 |
| pothole_6.jpg | partial | 1 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 180.2 |
| pothole_6.jpg | partial | 2 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 169.3 |
| pothole_6.jpg | not_fixed | 0 | NOT_FIXED | NEEDS_REVIEW | none | 189.0 |
| pothole_6.jpg | not_fixed | 1 | NOT_FIXED | NEEDS_REVIEW | none | 172.0 |
| pothole_6.jpg | not_fixed | 2 | NOT_FIXED | NEEDS_REVIEW | none | 188.3 |
| pothole_6.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 96.5 |
| pothole_6.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 96.2 |
| pothole_6.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 98.1 |
| pothole_6.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 175.8 |
| pothole_6.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 175.2 |
| pothole_6.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 169.3 |
| pothole_7.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 336.7 |
| pothole_7.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 336.6 |
| pothole_7.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 332.8 |
| pothole_7.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 330.1 |
| pothole_7.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 340.3 |
| pothole_7.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 336.5 |
| pothole_7.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 344.4 |
| pothole_7.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 337.3 |
| pothole_7.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 322.9 |
| pothole_7.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 102.4 |
| pothole_7.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 105.7 |
| pothole_7.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 106.5 |
| pothole_7.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 341.8 |
| pothole_7.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 333.0 |
| pothole_7.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 335.7 |
| pothole_9.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 533.7 |
| pothole_9.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 522.3 |
| pothole_9.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 521.6 |
| pothole_9.jpg | partial | 0 | PARTIAL | PARTIAL | defect_mask | 517.6 |
| pothole_9.jpg | partial | 1 | PARTIAL | PARTIAL | defect_mask | 529.0 |
| pothole_9.jpg | partial | 2 | PARTIAL | PARTIAL | defect_mask | 525.0 |
| pothole_9.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 532.4 |
| pothole_9.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 520.8 |
| pothole_9.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 536.3 |
| pothole_9.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 92.3 |
| pothole_9.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 96.9 |
| pothole_9.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 97.3 |
| pothole_9.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 528.9 |
| pothole_9.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 532.3 |
| pothole_9.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 526.5 |
| pothole_10.jpg | fixed | 0 | FIXED | NEEDS_REVIEW | ellipse_fallback | 207.4 |
| pothole_10.jpg | fixed | 1 | FIXED | NEEDS_REVIEW | ellipse_fallback | 210.5 |
| pothole_10.jpg | fixed | 2 | FIXED | NEEDS_REVIEW | ellipse_fallback | 214.6 |
| pothole_10.jpg | partial | 0 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 206.7 |
| pothole_10.jpg | partial | 1 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 210.0 |
| pothole_10.jpg | partial | 2 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 210.2 |
| pothole_10.jpg | not_fixed | 0 | NOT_FIXED | NEEDS_REVIEW | none | 212.2 |
| pothole_10.jpg | not_fixed | 1 | NOT_FIXED | NEEDS_REVIEW | none | 208.8 |
| pothole_10.jpg | not_fixed | 2 | NOT_FIXED | NEEDS_REVIEW | none | 213.3 |
| pothole_10.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 96.9 |
| pothole_10.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 99.5 |
| pothole_10.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 97.6 |
| pothole_10.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 209.2 |
| pothole_10.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 209.0 |
| pothole_10.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 211.5 |

Each pair is evaluated independently. Duplicate cases register the identical after image under a different complaint ID; no other test hashes contaminate repair scores.
Three deterministic jitter seeds are used for every photo/type. Wrong-location pairs use another road photo and GPS approximately 140 m away.

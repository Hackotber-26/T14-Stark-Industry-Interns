# Simulated-pair evaluation

All after images are simulated repairs or deliberately mismatched/reused evidence. This measures synthetic consistency, not real-world repair accuracy.

Mask mode: `auto`. Marked ROIs are supplied; optional YOLO suggestions are not required.
Planned: 120; completed: 120; errors: 0; unattempted: 0.

Accuracy on completed pairs: 67/120 (55.8%).
Average verification time: 142.9 ms.

| Expected / predicted | FIXED | PARTIAL | NOT_FIXED | SUSPICIOUS | NEEDS_REVIEW |
|---|---:|---:|---:|---:|---:|
| FIXED | 7 | 3 | 2 | 0 | 12 |
| PARTIAL | 1 | 1 | 10 | 0 | 12 |
| NOT_FIXED | 0 | 1 | 11 | 0 | 12 |
| SUSPICIOUS | 0 | 0 | 0 | 48 | 0 |
| NEEDS_REVIEW | 0 | 0 | 0 | 0 | 0 |

| Photo | Type | Seed | Expected | Actual / error | Mask | ms |
|---|---|---:|---|---|---|---:|
| pothole_1.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 288.4 |
| pothole_1.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 120.5 |
| pothole_1.jpg | fixed | 2 | FIXED | FIXED | defect_mask | 124.1 |
| pothole_1.jpg | partial | 0 | PARTIAL | NOT_FIXED | defect_mask | 126.3 |
| pothole_1.jpg | partial | 1 | PARTIAL | NOT_FIXED | defect_mask | 124.7 |
| pothole_1.jpg | partial | 2 | PARTIAL | NOT_FIXED | defect_mask | 123.4 |
| pothole_1.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 122.6 |
| pothole_1.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 122.2 |
| pothole_1.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 122.5 |
| pothole_1.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 91.2 |
| pothole_1.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 93.2 |
| pothole_1.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 97.6 |
| pothole_1.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 119.5 |
| pothole_1.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 120.6 |
| pothole_1.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 121.7 |
| pothole_2.jpg | fixed | 0 | FIXED | NEEDS_REVIEW | defect_mask | 163.4 |
| pothole_2.jpg | fixed | 1 | FIXED | NEEDS_REVIEW | defect_mask | 150.7 |
| pothole_2.jpg | fixed | 2 | FIXED | NEEDS_REVIEW | defect_mask | 155.7 |
| pothole_2.jpg | partial | 0 | PARTIAL | NEEDS_REVIEW | defect_mask | 152.6 |
| pothole_2.jpg | partial | 1 | PARTIAL | NEEDS_REVIEW | defect_mask | 151.5 |
| pothole_2.jpg | partial | 2 | PARTIAL | NEEDS_REVIEW | defect_mask | 165.1 |
| pothole_2.jpg | not_fixed | 0 | NOT_FIXED | NEEDS_REVIEW | none | 167.5 |
| pothole_2.jpg | not_fixed | 1 | NOT_FIXED | NEEDS_REVIEW | none | 169.0 |
| pothole_2.jpg | not_fixed | 2 | NOT_FIXED | NEEDS_REVIEW | none | 159.3 |
| pothole_2.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 116.0 |
| pothole_2.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 101.1 |
| pothole_2.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 101.3 |
| pothole_2.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 154.3 |
| pothole_2.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 154.6 |
| pothole_2.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 159.2 |
| pothole_4.jpg | fixed | 0 | FIXED | NEEDS_REVIEW | ellipse_fallback | 149.4 |
| pothole_4.jpg | fixed | 1 | FIXED | NEEDS_REVIEW | ellipse_fallback | 156.2 |
| pothole_4.jpg | fixed | 2 | FIXED | NEEDS_REVIEW | ellipse_fallback | 153.2 |
| pothole_4.jpg | partial | 0 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 157.9 |
| pothole_4.jpg | partial | 1 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 150.6 |
| pothole_4.jpg | partial | 2 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 151.8 |
| pothole_4.jpg | not_fixed | 0 | NOT_FIXED | NEEDS_REVIEW | none | 151.2 |
| pothole_4.jpg | not_fixed | 1 | NOT_FIXED | NEEDS_REVIEW | none | 150.9 |
| pothole_4.jpg | not_fixed | 2 | NOT_FIXED | NEEDS_REVIEW | none | 152.9 |
| pothole_4.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 95.2 |
| pothole_4.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 99.1 |
| pothole_4.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 97.6 |
| pothole_4.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 146.3 |
| pothole_4.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 153.9 |
| pothole_4.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 152.8 |
| pothole_5.jpg | fixed | 0 | FIXED | FIXED | defect_mask | 164.4 |
| pothole_5.jpg | fixed | 1 | FIXED | FIXED | defect_mask | 161.7 |
| pothole_5.jpg | fixed | 2 | FIXED | PARTIAL | defect_mask | 167.1 |
| pothole_5.jpg | partial | 0 | PARTIAL | NOT_FIXED | defect_mask | 166.8 |
| pothole_5.jpg | partial | 1 | PARTIAL | NOT_FIXED | defect_mask | 172.5 |
| pothole_5.jpg | partial | 2 | PARTIAL | NOT_FIXED | defect_mask | 179.7 |
| pothole_5.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 170.8 |
| pothole_5.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 168.0 |
| pothole_5.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 182.9 |
| pothole_5.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 104.9 |
| pothole_5.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 106.4 |
| pothole_5.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 104.4 |
| pothole_5.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | defect_mask | 162.8 |
| pothole_5.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | defect_mask | 162.9 |
| pothole_5.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | defect_mask | 168.1 |
| pothole_6.jpg | fixed | 0 | FIXED | NEEDS_REVIEW | ellipse_fallback | 140.0 |
| pothole_6.jpg | fixed | 1 | FIXED | NEEDS_REVIEW | ellipse_fallback | 142.3 |
| pothole_6.jpg | fixed | 2 | FIXED | NEEDS_REVIEW | ellipse_fallback | 139.7 |
| pothole_6.jpg | partial | 0 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 139.9 |
| pothole_6.jpg | partial | 1 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 141.4 |
| pothole_6.jpg | partial | 2 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 138.4 |
| pothole_6.jpg | not_fixed | 0 | NOT_FIXED | NEEDS_REVIEW | none | 144.9 |
| pothole_6.jpg | not_fixed | 1 | NOT_FIXED | NEEDS_REVIEW | none | 142.7 |
| pothole_6.jpg | not_fixed | 2 | NOT_FIXED | NEEDS_REVIEW | none | 141.4 |
| pothole_6.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 94.6 |
| pothole_6.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 95.7 |
| pothole_6.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 118.2 |
| pothole_6.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 139.2 |
| pothole_6.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 149.1 |
| pothole_6.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 138.8 |
| pothole_7.jpg | fixed | 0 | FIXED | NOT_FIXED | ellipse_fallback | 169.9 |
| pothole_7.jpg | fixed | 1 | FIXED | NOT_FIXED | ellipse_fallback | 168.4 |
| pothole_7.jpg | fixed | 2 | FIXED | FIXED | ellipse_fallback | 162.5 |
| pothole_7.jpg | partial | 0 | PARTIAL | NOT_FIXED | ellipse_fallback | 167.7 |
| pothole_7.jpg | partial | 1 | PARTIAL | NOT_FIXED | ellipse_fallback | 174.8 |
| pothole_7.jpg | partial | 2 | PARTIAL | FIXED | ellipse_fallback | 170.7 |
| pothole_7.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 165.2 |
| pothole_7.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 167.8 |
| pothole_7.jpg | not_fixed | 2 | NOT_FIXED | NOT_FIXED | none | 165.5 |
| pothole_7.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 104.0 |
| pothole_7.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 108.3 |
| pothole_7.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 110.6 |
| pothole_7.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 167.8 |
| pothole_7.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 169.7 |
| pothole_7.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 161.4 |
| pothole_9.jpg | fixed | 0 | FIXED | NEEDS_REVIEW | ellipse_fallback | 143.5 |
| pothole_9.jpg | fixed | 1 | FIXED | NEEDS_REVIEW | ellipse_fallback | 146.4 |
| pothole_9.jpg | fixed | 2 | FIXED | NEEDS_REVIEW | ellipse_fallback | 144.9 |
| pothole_9.jpg | partial | 0 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 149.4 |
| pothole_9.jpg | partial | 1 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 145.5 |
| pothole_9.jpg | partial | 2 | PARTIAL | NEEDS_REVIEW | ellipse_fallback | 143.6 |
| pothole_9.jpg | not_fixed | 0 | NOT_FIXED | NEEDS_REVIEW | none | 147.8 |
| pothole_9.jpg | not_fixed | 1 | NOT_FIXED | NEEDS_REVIEW | none | 150.0 |
| pothole_9.jpg | not_fixed | 2 | NOT_FIXED | NEEDS_REVIEW | none | 147.7 |
| pothole_9.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 101.7 |
| pothole_9.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 98.2 |
| pothole_9.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 98.7 |
| pothole_9.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 155.2 |
| pothole_9.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 146.7 |
| pothole_9.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 144.9 |
| pothole_10.jpg | fixed | 0 | FIXED | FIXED | ellipse_fallback | 145.5 |
| pothole_10.jpg | fixed | 1 | FIXED | PARTIAL | ellipse_fallback | 147.3 |
| pothole_10.jpg | fixed | 2 | FIXED | PARTIAL | ellipse_fallback | 147.1 |
| pothole_10.jpg | partial | 0 | PARTIAL | PARTIAL | ellipse_fallback | 161.7 |
| pothole_10.jpg | partial | 1 | PARTIAL | NOT_FIXED | ellipse_fallback | 189.0 |
| pothole_10.jpg | partial | 2 | PARTIAL | NOT_FIXED | ellipse_fallback | 150.6 |
| pothole_10.jpg | not_fixed | 0 | NOT_FIXED | NOT_FIXED | none | 153.5 |
| pothole_10.jpg | not_fixed | 1 | NOT_FIXED | NOT_FIXED | none | 149.6 |
| pothole_10.jpg | not_fixed | 2 | NOT_FIXED | PARTIAL | none | 152.2 |
| pothole_10.jpg | wrong_location | 0 | SUSPICIOUS | SUSPICIOUS | none | 101.6 |
| pothole_10.jpg | wrong_location | 1 | SUSPICIOUS | SUSPICIOUS | none | 99.8 |
| pothole_10.jpg | wrong_location | 2 | SUSPICIOUS | SUSPICIOUS | none | 100.7 |
| pothole_10.jpg | duplicate | 0 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 148.6 |
| pothole_10.jpg | duplicate | 1 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 148.5 |
| pothole_10.jpg | duplicate | 2 | SUSPICIOUS | SUSPICIOUS | ellipse_fallback | 150.2 |

Each pair is evaluated independently. Duplicate cases register the identical after image under a different complaint ID; no other test hashes contaminate repair scores.
Three deterministic jitter seeds are used for every photo/type. Wrong-location pairs use another road photo and GPS approximately 140 m away.

# Simulated-pair evaluation

All after images are simulated repairs or deliberately mismatched/reused evidence. This measures synthetic consistency, not real-world repair accuracy.

Mask mode: `auto`. Marked ROIs are supplied; optional YOLO suggestions are not required.
Planned: 120; completed: 0; errors: 1; unattempted: 119.

Accuracy and average verification time: unavailable (no completed predictions).

| Photo | Type | Seed | Expected | Actual / error | Mask | ms |
|---|---|---:|---|---|---|---:|
| pothole_1.jpg | fixed | 0 | FIXED | BLOCKED: pending pipeline implementation (NotImplementedError) | ellipse_fallback | 304.1 |

Each pair is evaluated independently. Duplicate cases register the identical after image under a different complaint ID; no other test hashes contaminate repair scores.
Three deterministic jitter seeds are used for every photo/type. Wrong-location pairs use another road photo and GPS approximately 140 m away.

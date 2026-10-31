MAX_SIDE = 1024            # resize both images so the longest side is <= this before processing

# Location
GPS_PASS_M = 30.0
GPS_WARN_M = 75.0          # 30–75 m = warn, > 75 m = fail

# Scene match (SIFT + RANSAC)
SIFT_FEATURES = 4000
LOWE_RATIO = 0.75
RANSAC_REPROJ = 5.0
MIN_GOOD_MATCHES = 12
SCENE_MIN_INLIERS = 25
SCENE_MIN_INLIER_RATIO = 0.25
H_DET_MIN, H_DET_MAX = 0.2, 5.0   # reject degenerate homographies

# Duplicate
PHASH_DUP_MAX_HAMMING = 6

# Model suggestion (optional helper only)
SEG_SUGGEST_CONF = 0.50    # only suggest a box when the model is at least this confident
SEG_IMGSZ = 640
ROI_PAD = 0.10             # pad the suggested box by 10% each side

# Defect measurement inside the marked box
RING_PX = 60               # width of the "surrounding road" ring around the box
TEXTURE_WIN = 7            # window for local texture (std of L channel)
ANOMALY_Z = 2.5            # pixel is "not road" if its robust z-score vs the ring is above this
TEXTURE_WEIGHT = 0.5       # texture counts half as much as colour
MIN_DEFECT_FRAC_OF_ROI = 0.05   # before-defect area / box area below this -> NEEDS_REVIEW
REMAINING_DILATE_PX = 7    # heatmap: grow remaining damage slightly before marking the rest repaired
GRABCUT_ITERS = 5          # iterations for segmenting the damage inside the marked box
MIN_DEFECT_CONTRAST = 8.0  # Lab distance between damage and surrounding road...
MIN_TEXTURE_CONTRAST = 0.35  # ...or surface texture differs from the road by at least 35%; below both -> no clear damage
CHANGE_THRESHOLD = 8.0     # Lab change below this (after lighting match) = surface unchanged
ROAD_LIKE_MIN = 12.0        # repaired pixels must be within this Lab distance of the road colour...
ROAD_LIKE_SCALE = 1.6      # ...or within 1.6x the road's own 95th-percentile spread, whichever is larger

# Verdict
FIXED_MIN_PCT = 85.0
PARTIAL_MIN_PCT = 25.0
QUALITY_GOOD = 0.60
QUALITY_POOR = 0.35

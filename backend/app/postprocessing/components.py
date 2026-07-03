import cv2
import numpy as np

def extract_connected_components(binary_mask: np.ndarray, min_area: int = 50):
    """
    Finds connected components in the binary mask.
    Filters out regions smaller than min_area.
    Returns a list of dicts with bbox and area for each valid region.
    """
    # Morphological operations to reduce false positives (thin lines from minor shifts)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    
    # Opening (erosion followed by dilation) removes small noise
    mask_cleaned = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
    
    # Closing (dilation followed by erosion) closes small holes
    mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_cleaned, connectivity=8)
    
    regions = []
    # label 0 is background
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            
            # Additional filter: skip very thin lines (width or height <= 2)
            if w <= 2 or h <= 2:
                continue
                
            regions.append({
                "label": i,
                "area": int(area),
                "bbox": [int(x), int(y), int(w), int(h)],
                "centroid": (float(centroids[i][0]), float(centroids[i][1]))
            })
            
    return regions

import numpy as np

def calculate_severity(area: int, total_area: int) -> str:
    percentage = (area / total_area) * 100
    if percentage > 5.0:
        return "High"
    elif percentage > 1.0:
        return "Medium"
    return "Low"

def get_location_string(centroid: tuple, width: int, height: int) -> str:
    cx, cy = centroid
    horizontal = "left" if cx < width / 3 else ("right" if cx > 2 * width / 3 else "center")
    vertical = "upper" if cy < height / 3 else ("lower" if cy > 2 * height / 3 else "middle")
    
    if horizontal == "center" and vertical == "middle":
        return "center"
    return f"{vertical}-{horizontal}"

def compute_statistics(regions: list, binary_mask: np.ndarray, prob_map: np.ndarray) -> dict:
    """
    Computes overall statistics and region-specific metadata.
    """
    height, width = binary_mask.shape
    total_area = height * width
    
    total_changed_area = sum(r['area'] for r in regions)
    percentage_changed = (total_changed_area / total_area) * 100
    
    formatted_regions = []
    for idx, r in enumerate(regions, start=1):
        # Get mean confidence for this region
        x, y, w, h = r['bbox']
        region_prob = prob_map[y:y+h, x:x+w]
        region_mask = binary_mask[y:y+h, x:x+w]
        
        # Only compute confidence over the actual pixels in the mask for this region
        # For simplicity, we just use the bounding box mean for now if it's mostly filled
        confidence = float(np.mean(region_prob))
        
        formatted_regions.append({
            "id": idx,
            "location": get_location_string(r['centroid'], width, height),
            "area": r['area'],
            "severity": calculate_severity(r['area'], total_area),
            "confidence": round(confidence, 3),
            "bbox": r['bbox']
        })
        
    return {
        "changed_regions": len(regions),
        "percentage": round(percentage_changed, 2),
        "regions": formatted_regions
    }

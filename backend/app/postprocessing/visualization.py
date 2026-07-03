import cv2
import numpy as np

def draw_bounding_boxes(image: np.ndarray, regions: list) -> np.ndarray:
    """Draws red bounding boxes on the image and labels them with their region ID."""
    result = image.copy()
    for r in regions:
        # Note: 'bbox' might be in r if called with original regions, or might have 'id' if called with formatted_regions.
        # routes.py passes stats_json['regions'] which has 'id' and 'bbox'.
        x, y, w, h = r['bbox']
        
        # Draw bounding box
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # Draw ID if available
        if 'id' in r:
            text = str(r['id'])
            # Calculate text size for background box
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            thickness = 2
            (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            
            # Draw background box for text
            cv2.rectangle(result, (x, y - text_h - baseline - 5), (x + text_w + 10, y), (0, 0, 255), -1)
            # Draw text
            cv2.putText(result, text, (x + 5, y - 5), font, font_scale, (255, 255, 255), thickness)
            
    return result

def create_heatmap(prob_map: np.ndarray) -> np.ndarray:
    """Converts a probability map [0,1] to a colormap (BGR)."""
    # Normalize to 0-255
    heatmap_gray = np.uint8(255 * prob_map)
    # Apply JET colormap
    heatmap = cv2.applyColorMap(heatmap_gray, cv2.COLORMAP_JET)
    return heatmap

def create_overlay(image: np.ndarray, binary_mask: np.ndarray, color=(0, 0, 255), alpha=0.5) -> np.ndarray:
    """Overlays the binary mask on the image with a specific color."""
    overlay = image.copy()
    
    # Create a colored mask
    colored_mask = np.zeros_like(image)
    colored_mask[binary_mask > 0] = color
    
    # Blend where mask is active
    active = binary_mask > 0
    overlay[active] = cv2.addWeighted(image[active], 1 - alpha, colored_mask[active], alpha, 0)
    
    return overlay

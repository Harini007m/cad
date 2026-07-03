import cv2
import numpy as np

def detailed_cad_compare(img1: np.ndarray, img2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Performs a high-resolution detailed comparison of two CAD images.
    Returns:
        binary_mask: (H, W) uint8 array (0 or 255) indicating changes
        prob_map: (H, W) float32 array (0.0 to 1.0) indicating difference magnitude
    """
    # Convert to grayscale for structural comparison
    g1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Apply a slight Gaussian blur to account for minor sub-pixel shifts and anti-aliasing.
    # This prevents false positives along the edges of identical lines that are just shifted by 1 pixel.
    b1 = cv2.GaussianBlur(g1, (5, 5), 0)
    b2 = cv2.GaussianBlur(g2, (5, 5), 0)
    
    # Compute absolute pixel difference
    diff = cv2.absdiff(b1, b2)
    
    # Threshold the difference. CAD drawings are high contrast (black lines on white).
    # A threshold of 35 catches significant structural differences while ignoring slight blur differences.
    _, binary_mask = cv2.threshold(diff, 35, 255, cv2.THRESH_BINARY)
    
    # Normalize diff for the heatmap / probability map
    prob_map = diff.astype(np.float32) / 255.0
    
    return binary_mask, prob_map

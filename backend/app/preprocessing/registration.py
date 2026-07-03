import cv2
import numpy as np

def align_images(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """
    Aligns img2 to match img1 using ORB feature matching.
    Returns the aligned version of img2.
    """
    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Initialize ORB detector
    MAX_FEATURES = 5000
    orb = cv2.ORB_create(MAX_FEATURES)
    
    # Detect ORB features and compute descriptors
    keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)
    
    # Match features
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)
    
    # Sort matches by score
    matches = sorted(matches, key=lambda x: x.distance)
    
    # Keep top 10%
    keep = int(len(matches) * 0.1)
    if keep == 0:
        return img2 # Fallback if no matches
    matches = matches[:keep]
    
    # Extract location of good matches
    pts1 = np.zeros((len(matches), 2), dtype=np.float32)
    pts2 = np.zeros((len(matches), 2), dtype=np.float32)
    
    for i, match in enumerate(matches):
        pts1[i, :] = keypoints1[match.queryIdx].pt
        pts2[i, :] = keypoints2[match.trainIdx].pt
        
    # Find homography
    h, mask = cv2.findHomography(pts2, pts1, cv2.RANSAC)
    
    # Use homography to warp img2
    if h is not None:
        height, width, channels = img1.shape
        aligned_img = cv2.warpPerspective(img2, h, (width, height), borderValue=(255, 255, 255))
        return aligned_img
    
    return img2 # Fallback

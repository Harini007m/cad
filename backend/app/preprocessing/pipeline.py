import cv2
import numpy as np
import albumentations as A

def resize_image(image: np.ndarray, target_size=(224, 224)) -> np.ndarray:
    return cv2.resize(image, (target_size[1], target_size[0]))

def resize_for_visualization(image: np.ndarray, max_dim=1500) -> np.ndarray:
    """
    Resizes image maintaining aspect ratio so the longest side is max_dim.
    If the image is smaller than max_dim, it returns the original image.
    """
    h, w = image.shape[:2]
    if max(h, w) <= max_dim:
        return image
        
    scale = max_dim / float(max(h, w))
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

def preprocess_image(image: np.ndarray, target_size=(224, 224)) -> np.ndarray:
    """
    Preprocess image: resize, normalize, color normalization.
    Assuming image is read in BGR format by OpenCV.
    Returns RGB normalized image.
    """
    # Handle single channel (grayscale)
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif len(image.shape) == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    else:
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    transform = A.Compose([
        A.Resize(height=target_size[0], width=target_size[1]),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ])
    
    augmented = transform(image=image)
    return augmented['image']

def read_image_from_path(path: str) -> np.ndarray:
    """Read image using OpenCV"""
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not read image at {path}")
    return img

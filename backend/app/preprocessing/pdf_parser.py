import fitz  # PyMuPDF
import cv2
import numpy as np

def convert_pdf_to_image(pdf_path: str, page_num: int = 0) -> np.ndarray:
    """
    Reads a PDF file and converts a specific page to an OpenCV image (BGR).
    """
    doc = fitz.open(pdf_path)
    if page_num >= len(doc):
        raise ValueError(f"Page {page_num} is out of bounds for PDF with {len(doc)} pages.")
        
    page = doc.load_page(page_num)
    # 300 DPI for high quality
    zoom = 300 / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    
    # Convert to numpy array
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    
    # PyMuPDF outputs RGB. Convert to BGR for OpenCV consistency
    if pix.n == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif pix.n == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
    return img

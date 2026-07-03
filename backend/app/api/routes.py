import os
import uuid
import shutil
import cv2
import numpy as np
from typing import List
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.config import settings
from ..models import schemas, domain

# Pipeline imports
from ..preprocessing import pipeline, pdf_parser, registration
from ..detection.cad_detector import detailed_cad_compare
from ..postprocessing import components, statistics, visualization
from ..summary.llm import generate_summary

router = APIRouter()

# No longer using the low-res ChangeDetector ViT for CAD drawings
# detector = ChangeDetector()

@router.post("/upload", response_model=dict)
async def upload_files(
    image_a: UploadFile = File(...),
    image_b: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file types
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if image_a.content_type not in allowed_types or image_b.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use JPG, PNG, or PDF.")
    
    # Save files
    result_id = str(uuid.uuid4())
    ext_a = image_a.filename.split('.')[-1]
    ext_b = image_b.filename.split('.')[-1]
    path_a = os.path.join(settings.UPLOADS_DIR, f"{result_id}_a.{ext_a}")
    path_b = os.path.join(settings.UPLOADS_DIR, f"{result_id}_b.{ext_b}")
    
    with open(path_a, "wb") as buffer:
        shutil.copyfileobj(image_a.file, buffer)
    with open(path_b, "wb") as buffer:
        shutil.copyfileobj(image_b.file, buffer)
        
    # Create DB record
    record = domain.ResultRecord(
        id=result_id,
        image_a_path=path_a,
        image_b_path=path_b,
        status="uploaded"
    )
    db.add(record)
    db.commit()
    
    return {"message": "Upload successful", "id": result_id}

def load_image(path: str) -> 'np.ndarray':
    if path.lower().endswith('.pdf'):
        return pdf_parser.convert_pdf_to_image(path)
    return cv2.imread(path)

@router.post("/compare/{result_id}", response_model=schemas.ResultResponse)
def compare_images(result_id: str, db: Session = Depends(get_db)):
    record = db.query(domain.ResultRecord).filter(domain.ResultRecord.id == result_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Result not found")
        
    try:
        record.status = "processing"
        db.commit()

        # 1. Load Images
        img1_raw = load_image(record.image_a_path)
        img2_raw = load_image(record.image_b_path)
        
        # 2. Align Raw Images
        img2_aligned_raw = registration.align_images(img1_raw, img2_raw)
        
        # 3. Preprocess for Detection Model
        img1_proc = pipeline.preprocess_image(img1_raw)
        img2_proc = pipeline.preprocess_image(img2_aligned_raw)
        
        # 4. Resize Original for Visualization
        img1_vis = pipeline.resize_for_visualization(img1_raw)
        img2_vis = pipeline.resize_for_visualization(img2_aligned_raw)
        
        # 5. Detection (High-Resolution CAD Comparison)
        # Using detailed_cad_compare which works directly on the 1500px images
        binary_mask, prob_map = detailed_cad_compare(img1_vis, img2_vis)
        
        # 6. Postprocessing (Connected components)
        # Set min_area to 150 to catch detailed changes while ignoring micro-noise
        regions = components.extract_connected_components(binary_mask, min_area=150)
        
        # 5. Statistics
        stats_json = statistics.compute_statistics(regions, binary_mask, prob_map)
        
        base_url = "/outputs"
        
        # 8. Generate Side-by-Side Crops for UI
        for r in stats_json['regions']:
            x, y, w, h = r['bbox']
            pad = 40
            y1, y2 = max(0, y - pad), min(img1_vis.shape[0], y + h + pad)
            x1, x2 = max(0, x - pad), min(img1_vis.shape[1], x + w + pad)
            
            crop_a = img1_vis[y1:y2, x1:x2]
            crop_b = img2_vis[y1:y2, x1:x2]
            
            crop_a_filename = f"{result_id}_crop_a_{r.get('id')}.jpg"
            crop_b_filename = f"{result_id}_crop_b_{r.get('id')}.jpg"
            
            cv2.imwrite(os.path.join(settings.OUTPUTS_DIR, crop_a_filename), crop_a)
            cv2.imwrite(os.path.join(settings.OUTPUTS_DIR, crop_b_filename), crop_b)
            
            r['crop_a_url'] = f"{base_url}/{crop_a_filename}"
            r['crop_b_url'] = f"{base_url}/{crop_b_filename}"
        
        # 8. Visualization
        bbox_img = visualization.draw_bounding_boxes(img1_vis.copy(), stats_json['regions'])
        heatmap_img = visualization.create_heatmap(prob_map)
        overlay_img = visualization.create_overlay(img1_vis.copy(), binary_mask)
        
        # Save output images
        original_vis_path_a = os.path.join(settings.OUTPUTS_DIR, f"{result_id}_original_vis_a.jpg")
        original_vis_path_b = os.path.join(settings.OUTPUTS_DIR, f"{result_id}_original_vis_b.jpg")
        bbox_path = os.path.join(settings.OUTPUTS_DIR, f"{result_id}_bbox.jpg")
        heatmap_path = os.path.join(settings.OUTPUTS_DIR, f"{result_id}_heatmap.jpg")
        overlay_path = os.path.join(settings.OUTPUTS_DIR, f"{result_id}_overlay.jpg")
        mask_path = os.path.join(settings.OUTPUTS_DIR, f"{result_id}_mask.png")
        
        cv2.imwrite(original_vis_path_a, img1_vis)
        cv2.imwrite(original_vis_path_b, img2_vis)
        cv2.imwrite(bbox_path, bbox_img)
        cv2.imwrite(heatmap_path, heatmap_img)
        cv2.imwrite(overlay_path, overlay_img)
        cv2.imwrite(mask_path, binary_mask)
        
        record.bbox_path = bbox_path
        record.heatmap_path = heatmap_path
        record.overlay_path = overlay_path
        record.mask_path = mask_path
        
        # 7. LLM Summary
        summary = generate_summary(stats_json)
        
        # 8. Update Record
        record.status = "completed"
        record.statistics = stats_json
        record.summary = summary
        db.commit()
        db.refresh(record)
        
    except Exception as e:
        record.status = f"failed: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
    
    # Build URLs for response
    # base_url is already defined earlier, but just in case:
    base_url = "/outputs"
    
    return schemas.ResultResponse(
        id=record.id,
        status=record.status,
        statistics=record.statistics,
        summary=record.summary,
        original_a_url=f"{base_url}/{os.path.basename(original_vis_path_a)}",
        original_b_url=f"{base_url}/{os.path.basename(original_vis_path_b)}",
        heatmap_url=f"{base_url}/{os.path.basename(heatmap_path)}",
        overlay_url=f"{base_url}/{os.path.basename(overlay_path)}",
        bbox_url=f"{base_url}/{os.path.basename(bbox_path)}"
    )

@router.get("/results/{result_id}", response_model=schemas.ResultResponse)
def get_result(result_id: str, db: Session = Depends(get_db)):
    record = db.query(domain.ResultRecord).filter(domain.ResultRecord.id == result_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Result not found")
    
    base_url = "/outputs"
    return schemas.ResultResponse(
        id=record.id,
        status=record.status,
        statistics=record.statistics,
        summary=record.summary,
        original_a_url=f"{base_url}/{result_id}_original_vis_a.jpg" if record.status == "completed" else "",
        original_b_url=f"{base_url}/{result_id}_original_vis_b.jpg" if record.status == "completed" else "",
        heatmap_url=f"{base_url}/{result_id}_heatmap.jpg" if record.status == "completed" else "",
        overlay_url=f"{base_url}/{result_id}_overlay.jpg" if record.status == "completed" else "",
        bbox_url=f"{base_url}/{result_id}_bbox.jpg" if record.status == "completed" else ""
    )

@router.get("/report/{result_id}")
def generate_report(result_id: str, db: Session = Depends(get_db)):
    record = db.query(domain.ResultRecord).filter(domain.ResultRecord.id == result_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Result not found")
        
    from ..reports.pdf_generator import create_pdf_report
    from fastapi.responses import FileResponse
    
    report_path = os.path.join(settings.OUTPUTS_DIR, f"{result_id}_report.pdf")
    
    if not os.path.exists(report_path):
        create_pdf_report(record, report_path)
        
    return FileResponse(report_path, media_type='application/pdf', filename=f"Report_{result_id}.pdf")

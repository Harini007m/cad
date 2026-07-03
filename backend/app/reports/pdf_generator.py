import os
import cv2
from fpdf import FPDF
from ..models import domain

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AI Change Detection Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf_report(record: domain.ResultRecord, output_path: str):
    pdf = PDFReport()
    pdf.add_page()
    
    # Metadata
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Report ID: {record.id}", 0, 1)
    pdf.cell(0, 10, f"Date: {record.created_at.strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    
    # Summary
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "AI Summary", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 10, record.summary or "No summary available.")
    
    # Statistics
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Statistics", 0, 1)
    pdf.set_font('Arial', '', 11)
    if record.statistics:
        pdf.cell(0, 10, f"Total Changed Regions: {record.statistics.get('changed_regions', 0)}", 0, 1)
        pdf.cell(0, 10, f"Percentage Changed: {record.statistics.get('percentage', 0.0)}%", 0, 1)
    
    # Images (Original A and Overlay)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Detection Overview", 0, 1)
        
    if record.overlay_path and os.path.exists(record.overlay_path):
        pdf.image(record.overlay_path, w=150)
        
    # Detailed Regions
    if record.statistics and 'regions' in record.statistics and len(record.statistics['regions']) > 0:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Detailed Changes", 0, 1)
        pdf.ln(5)
        
        base_dir = os.path.dirname(record.overlay_path) if record.overlay_path else "outputs"
        
        for r in record.statistics['regions']:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Change #{r.get('id', '?')}", 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, f"Location: {r.get('location')} | Severity: {r.get('severity')} | Area: {r.get('area')} px", 0, 1)
            
            crop_a_path = os.path.join(base_dir, f"{record.id}_crop_a_{r.get('id')}.jpg")
            crop_b_path = os.path.join(base_dir, f"{record.id}_crop_b_{r.get('id')}.jpg")
            
            if os.path.exists(crop_a_path) and os.path.exists(crop_b_path):
                # Read image to get aspect ratio
                crop_a = cv2.imread(crop_a_path)
                if crop_a is not None:
                    # Draw side by side
                    y_pos = pdf.get_y()
                    # Check page break
                    if y_pos > 200:
                        pdf.add_page()
                        y_pos = pdf.get_y()
                    
                    pdf.cell(80, 5, "Version 1 (Original)", 0, 0, 'C')
                    pdf.cell(80, 5, "Version 2 (Modified)", 0, 1, 'C')
                    
                    # Image widths
                    pdf.image(crop_a_path, x=20, y=pdf.get_y(), w=70)
                    pdf.image(crop_b_path, x=100, y=pdf.get_y(), w=70)
                    
                    # Advance Y based on image aspect ratio
                    aspect = crop_a.shape[0] / crop_a.shape[1]
                    pdf.set_y(pdf.get_y() + (70 * aspect) + 15)
                
    pdf.output(output_path)


from sqlalchemy import Column, String, Float, Integer, Text, JSON, DateTime
from sqlalchemy.orm import declarative_base
import datetime
import uuid

Base = declarative_base()

class ResultRecord(Base):
    __tablename__ = 'results'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="processing")
    
    # Paths to saved files
    image_a_path = Column(String, nullable=True)
    image_b_path = Column(String, nullable=True)
    heatmap_path = Column(String, nullable=True)
    overlay_path = Column(String, nullable=True)
    bbox_path = Column(String, nullable=True)
    mask_path = Column(String, nullable=True)

    # JSON statistics
    statistics = Column(JSON, nullable=True)
    
    # Generated summary
    summary = Column(Text, nullable=True)

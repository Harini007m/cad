from pydantic import BaseModel, Field
from typing import List, Optional

class RegionInfo(BaseModel):
    location: str
    area: int
    severity: str
    confidence: float
    bbox: List[int]

class Statistics(BaseModel):
    changed_regions: int
    percentage: float
    regions: List[RegionInfo]

class ResultResponse(BaseModel):
    id: str
    status: str
    statistics: Optional[Statistics] = None
    summary: Optional[str] = None
    original_a_url: Optional[str] = None
    original_b_url: Optional[str] = None
    heatmap_url: Optional[str] = None
    overlay_url: Optional[str] = None
    bbox_url: Optional[str] = None

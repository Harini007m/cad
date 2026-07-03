import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.routes import router as api_router
from .core.database import engine
from .models import domain
from .core.config import settings

# Create DB tables
domain.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Based Image Difference Detection API",
    description="API for detecting, visualizing, and summarizing changes between two images.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for outputs
app.mount("/outputs", StaticFiles(directory=settings.OUTPUTS_DIR), name="outputs")
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Image Difference Detection API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


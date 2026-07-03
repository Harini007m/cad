import requests
import json
from ..core.config import settings

def generate_summary(statistics: dict) -> str:
    """
    Passes the statistics JSON to the local LLM via Ollama 
    and returns a concise technical summary.
    """
    # Remove large bounding box arrays from the prompt to save context and prevent hallucination
    clean_stats = {
        "changed_regions": statistics["changed_regions"],
        "percentage": statistics["percentage"],
        "regions": [
            {
                "id": r["id"],
                "location": r["location"], 
                "area": r["area"], 
                "severity": r["severity"], 
                "confidence": r["confidence"]
            } 
            for r in statistics["regions"]
        ]
    }
    
    prompt = f"""
You are an expert AI inspector for Architectural and CAD drawings. 
Based on the following JSON data of detected changes between two CAD floor plans, write a concise, professional technical summary describing the modifications. 
Changes in CAD often represent structural modifications like door sizes, window placements, wall lengths, or moved objects.
Each change has an "id" which corresponds to its numbered bounding box in the report. Please refer to changes by their ID (e.g., "Change #1 appears to be a modification in the upper-left area...").
Do not hallucinate any information not present in the JSON.

JSON Data:
{json.dumps(clean_stats, indent=2)}

Summary:
"""

    payload = {
        "model": settings.LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(settings.OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Could not generate summary.")
    except Exception as e:
        print(f"Error communicating with LLM: {e}")
        # Fallback summary
        num_changes = clean_stats["changed_regions"]
        pct = clean_stats["percentage"]
        return f"The comparison detected {num_changes} significant modifications. Approximately {pct}% of the image has changed."

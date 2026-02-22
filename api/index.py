import os
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(redirect_slashes=False)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

def load_data():
    # Vercel's root is usually the base of your GitHub repo
    # Try looking for it in the root first
    paths_to_try = [
        os.path.join(os.getcwd(), "telemetry.csv"),
        os.path.join(os.path.dirname(__file__), "..", "telemetry.csv"),
        "telemetry.csv"
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return pd.read_csv(path)
    return None

@app.post("/api/metrics")
async def get_metrics(payload: dict):
    df = load_data()
    
    if df is None:
        return {"error": "telemetry.csv not found in root directory"}

    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)
    results = {}

    for reg in regions:
        # Normalize column names to lowercase just in case
        df.columns = [c.lower() for c in df.columns]
        subset = df[df['region'] == reg]
        
        if not subset.empty:
            results[reg] = {
                "avg_latency": round(subset['latency'].mean(), 2),
                "p95_latency": round(subset['latency'].quantile(0.95), 2),
                "avg_uptime": round(subset['uptime'].mean(), 3),
                "breaches": int((subset['latency'] > threshold).sum())
            }
            
    return results

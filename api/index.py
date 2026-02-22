import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

# redirect_slashes=False prevents 404s if you forget the last "/"
app = FastAPI(redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Use absolute path to find the CSV regardless of where the script runs
CURR_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(CURR_DIR, "..", "telemetry.csv")

@app.post("/api/metrics")
async def get_metrics(payload: dict):
    # If this fails, check Vercel Logs for "FileNotFoundError"
    df = pd.read_csv(CSV_PATH)
    
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)
    results = {}

    for reg in regions:
        subset = df[df['region'] == reg]
        if not subset.empty:
            results[reg] = {
                "avg_latency": round(subset['latency'].mean(), 2),
                "p95_latency": round(subset['latency'].quantile(0.95), 2),
                "avg_uptime": round(subset['uptime'].mean(), 3),
                "breaches": int((subset['latency'] > threshold).sum())
            }
    return results

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Enable CORS for dashboards
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST"], allow_headers=["*"])

@app.post("/api/metrics")
async def get_metrics(payload: dict):
    # Load your telemetry bundle (ensure this file is in your GitHub root)
    df = pd.read_csv("telemetry.csv") 
    
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

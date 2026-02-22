import os
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# This finds the CSV in your root folder correctly on Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "telemetry.csv")

@app.post("/api/metrics")
async def get_metrics(payload: dict):
    # Use the absolute path we created above
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        return {"error": f"CSV not found at {CSV_PATH}. Check GitHub root."}

    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)
    results = {}

    for reg in regions:
        # subset the data for the specific region
        subset = df[df['region'] == reg]
        if not subset.empty:
            results[reg] = {
                "avg_latency": round(float(subset['latency'].mean()), 2),
                "p95_latency": round(float(subset['latency'].quantile(0.95)), 2),
                "avg_uptime": round(float(subset['uptime'].mean()), 3),
                "breaches": int((subset['latency'] > threshold).sum())
            }
    return results

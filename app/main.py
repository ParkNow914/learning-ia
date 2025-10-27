"""API FastAPI para o sistema de Knowledge Tracing."""
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import pandas as pd
import torch
from dkt_model import load_model
from recommender import recommend_next

# Rate limiting simples em memória
rate_limit_store = {}

app = FastAPI(title="Knowledge Tracing API", version="1.0.0")

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    handlers=[logging.FileHandler("results/logs/api.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def check_api_key(x_api_key: Optional[str]):
    expected_key = os.getenv('SECRET_API_KEY', 'troque_aqui')
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

def check_rate_limit(request: Request):
    ip = request.client.host
    now = datetime.now()
    if ip not in rate_limit_store:
        rate_limit_store[ip] = []
    
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if (now - t).seconds < 60]
    
    limit = int(os.getenv('RATE_LIMIT_PER_MIN', 60))
    if len(rate_limit_store[ip]) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limit_store[ip].append(now)

class InferRequest(BaseModel):
    student_history: List[Dict]
    candidate_items: List[str]
    strategy: str = 'target'
    target_p: float = 0.7

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), x_api_key: str = Header(None), request: Request = None):
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    Path('uploads').mkdir(exist_ok=True)
    filepath = Path('uploads') / file.filename
    
    content = await file.read()
    filepath.write_bytes(content)
    
    try:
        df = pd.read_csv(filepath)
        required = ['student_id', 'timestamp', 'item_id', 'skill_id', 'correct']
        if not all(col in df.columns for col in required):
            raise HTTPException(status_code=400, detail=f"Missing required columns: {required}")
        
        return {
            'n_students': int(df['student_id'].nunique()),
            'n_items': int(df['item_id'].nunique()),
            'sample_rows': df.head(5).to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/train")
async def train_model(epochs: int = 3, batch_size: int = 32, x_api_key: str = Header(None), request: Request = None):
    check_api_key(x_api_key)
    check_rate_limit(request)
    return {"status": "Training would start here", "epochs": epochs, "batch_size": batch_size}

@app.post("/infer")
async def infer(req: InferRequest, x_api_key: str = Header(None), request: Request = None):
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    try:
        model, metadata = load_model('models/dkt.pt')
        item_to_idx = metadata.get('item_to_idx', {})
        
        recommendation = recommend_next(
            req.student_history, model, req.candidate_items, item_to_idx,
            target_p=req.target_p, strategy=req.strategy
        )
        
        return recommendation
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found. Train first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics(x_api_key: str = Header(None), request: Request = None):
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    try:
        with open('results/summary.json') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Metrics not found")

@app.get("/model")
async def download_model(x_api_key: str = Header(None), request: Request = None):
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    model_path = 'models/dkt.pt'
    if not Path(model_path).exists():
        raise HTTPException(status_code=404, detail="Model not found")
    
    return FileResponse(model_path, headers={'X-Model-Version': 'v1.0.0'})

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

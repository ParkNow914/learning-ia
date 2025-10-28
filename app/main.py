"""API FastAPI para o sistema de Knowledge Tracing."""

import os
import json
import logging
import secrets
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import torch
from dkt_model import load_model
from recommender import recommend_next

# Importar features avançadas
try:
    from dkt_model_advanced import DKTModelAdvanced
    from utils.drift_detection import DriftDetector
    from utils.optimization import PredictionCache
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    logging.warning("Features avançadas não disponíveis")

# Rate limiting simples em memória
rate_limit_store = {}

# Inicializar features avançadas
prediction_cache = PredictionCache() if ADVANCED_FEATURES else None
drift_detector = DriftDetector() if ADVANCED_FEATURES else None

app = FastAPI(
    title="Knowledge Tracing API",
    version="2.2.0",
    description="API para sistema de Knowledge Tracing com features avançadas",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Adicionar compressão GZIP (melhora performance)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configurar CORS para permitir acesso do frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    handlers=[logging.FileHandler("results/logs/api.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# Constantes de validação de upload
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".csv"}
ALLOWED_MIME_TYPES = {"text/csv", "text/plain", "application/csv"}


async def validate_upload(file: UploadFile) -> bytes:
    """Valida arquivo de upload para segurança."""
    # 1. Validar extensão
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"❌ Extensão não permitida: {ext}. Use: {ALLOWED_EXTENSIONS}"
        )
    
    # 2. Ler conteúdo
    content = await file.read()
    file_size = len(content)
    
    # 3. Validar tamanho
    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"❌ Arquivo muito grande: {file_size/1024/1024:.2f}MB. Máximo: {MAX_UPLOAD_SIZE/1024/1024}MB"
        )
    
    # 4. Validar MIME type (se disponível)
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"MIME type suspeito: {file.content_type} para arquivo {file.filename}")
    
    # 5. Validar que não está vazio
    if file_size == 0:
        raise HTTPException(status_code=400, detail="❌ Arquivo vazio")
    
    return content


def check_api_key(x_api_key: Optional[str]):
    """Verifica API key de forma segura contra timing attacks."""
    expected_key = os.getenv("SECRET_API_KEY", "troque_aqui")
    # Usar secrets.compare_digest() para evitar timing attacks
    if not x_api_key or not secrets.compare_digest(x_api_key, expected_key):
        raise HTTPException(status_code=401, detail="Invalid API key")


def check_rate_limit(request: Request):
    ip = request.client.host
    now = datetime.now()
    if ip not in rate_limit_store:
        rate_limit_store[ip] = []

    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if (now - t).seconds < 60]

    limit = int(os.getenv("RATE_LIMIT_PER_MIN", 60))
    if len(rate_limit_store[ip]) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    rate_limit_store[ip].append(now)


class InferRequest(BaseModel):
    student_history: List[Dict]
    candidate_items: List[str]
    strategy: str = "target"
    target_p: float = 0.7


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), x_api_key: str = Header(None), request: Request = None):
    """Upload e validação de arquivo CSV com segurança."""
    check_api_key(x_api_key)
    check_rate_limit(request)

    # Validar arquivo antes de processar
    content = await validate_upload(file)

    Path("uploads").mkdir(exist_ok=True)
    filepath = Path("uploads") / file.filename

    filepath.write_bytes(content)

    try:
        df = pd.read_csv(filepath)
        required = ["student_id", "timestamp", "item_id", "skill_id", "correct"]
        if not all(col in df.columns for col in required):
            raise HTTPException(status_code=400, detail=f"Missing required columns: {required}")

        return {
            "n_students": int(df["student_id"].nunique()),
            "n_items": int(df["item_id"].nunique()),
            "sample_rows": df.head(5).to_dict("records"),
        }
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"❌ CSV inválido: {str(e)}")
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
        model, metadata = load_model("models/dkt.pt")
        item_to_idx = metadata.get("item_to_idx", {})

        recommendation = recommend_next(
            req.student_history, model, req.candidate_items, item_to_idx, target_p=req.target_p, strategy=req.strategy
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
        with open("results/summary.json") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Metrics not found")


@app.get("/model")
async def download_model(x_api_key: str = Header(None), request: Request = None):
    check_api_key(x_api_key)
    check_rate_limit(request)

    model_path = "models/dkt.pt"
    if not Path(model_path).exists():
        raise HTTPException(status_code=404, detail="Model not found")

    return FileResponse(model_path, headers={"X-Model-Version": "v1.0.0"})


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# ====================
# ENDPOINTS AVANÇADOS
# ====================

@app.post("/advanced/mc-dropout")
async def mc_dropout_inference(
    request_data: Dict,
    x_api_key: str = Header(None),
    request: Request = None
):
    """Inferência com MC Dropout para estimativa de incerteza."""
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    if not ADVANCED_FEATURES:
        raise HTTPException(
            status_code=501,
            detail="❌ Features avançadas não disponíveis. Instale dependências necessárias."
        )
    
    try:
        # Carregar modelo avançado
        model_path = "models/dkt.pt"
        if not Path(model_path).exists():
            raise HTTPException(status_code=404, detail="❌ Modelo não encontrado")
        
        # Carregar modelo avançado com MC Dropout
        checkpoint = torch.load(model_path, map_location='cpu')
        n_items = checkpoint.get("n_items", 50)
        n_skills = checkpoint.get("n_skills", 10)
        
        # Criar modelo avançado
        model = DKTModelAdvanced(
            n_items=n_items,
            n_skills=n_skills,
            hidden_size=checkpoint.get("hidden_size", 128),
            n_layers=checkpoint.get("n_layers", 2),
            use_mc_dropout=True,
            dropout_rate=0.3
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        
        # Preparar dados de entrada
        student_history = request_data.get("student_history", [])
        candidate_item = request_data.get("candidate_item", "item_0")
        n_samples = request_data.get("n_samples", 10)
        
        if not student_history:
            raise HTTPException(status_code=400, detail="❌ student_history não pode ser vazio")
        
        # Obter mapeamento de itens
        item_to_idx = checkpoint.get("item_to_idx", {})
        
        # Preparar sequência
        import torch
        seq_len = len(student_history)
        inputs = torch.zeros((1, seq_len, n_items * 2))
        
        for i, interaction in enumerate(student_history):
            item_id = interaction.get("item_id", "")
            correct = interaction.get("correct", 0)
            
            if item_id in item_to_idx:
                idx = item_to_idx[item_id]
                offset = n_items if correct else 0
                inputs[0, i, offset + idx] = 1
        
        # Executar MC Dropout
        mean_prob, std_prob = model.predict_with_uncertainty(
            inputs,
            n_samples=n_samples
        )
        
        # Calcular confiança
        if std_prob < 0.1:
            confidence = "alta"
        elif std_prob < 0.2:
            confidence = "média"
        else:
            confidence = "baixa"
        
        return {
            "mensagem": "✅ MC Dropout inference executado",
            "probabilidade_media": float(mean_prob),
            "incerteza_std": float(std_prob),
            "confianca": confidence,
            "n_samples": n_samples,
            "dica": f"Incerteza {'baixa' if std_prob < 0.1 else 'média' if std_prob < 0.2 else 'alta'} indica {'alta' if std_prob < 0.1 else 'média' if std_prob < 0.2 else 'baixa'} confiança na predição",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro em MC Dropout: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Erro: {str(e)}")


@app.post("/advanced/check-drift")
async def check_drift(
    file: UploadFile = File(...),
    x_api_key: str = Header(None),
    request: Request = None
):
    """Verifica drift entre dados de baseline e novos dados."""
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    if not ADVANCED_FEATURES or drift_detector is None:
        raise HTTPException(
            status_code=501,
            detail="❌ Drift detection não disponível"
        )
    
    try:
        # Carregar dados
        contents = await file.read()
        df_new = pd.read_csv(pd.io.common.BytesIO(contents))
        
        # Carregar baseline
        baseline_path = "data/real_combined_dataset.csv"
        if not Path(baseline_path).exists():
            raise HTTPException(
                status_code=404,
                detail="❌ Dados de baseline não encontrados"
            )
        
        df_baseline = pd.read_csv(baseline_path)
        
        # Verificar drift
        results = drift_detector.check_and_alert(df_baseline, df_new)
        
        return {
            "mensagem": "✅ Análise de drift concluída",
            "drift_detectado": results.get("drift_detected", False),
            "psi_score": results.get("psi", 0.0),
            "ks_statistic": results.get("ks_stat", 0.0),
            "recomendacao": results.get("action", "Nenhuma ação necessária"),
            "detalhes": results
        }
    except Exception as e:
        logger.error(f"Erro em check drift: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Erro: {str(e)}")


@app.get("/advanced/cache-stats")
async def get_cache_stats(
    x_api_key: str = Header(None),
    request: Request = None
):
    """Retorna estatísticas do cache de predições."""
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    if not ADVANCED_FEATURES or prediction_cache is None:
        raise HTTPException(
            status_code=501,
            detail="❌ Cache não disponível"
        )
    
    try:
        stats = prediction_cache.get_stats()
        
        return {
            "mensagem": "✅ Estatísticas do cache",
            "entradas_totais": stats.get("total_entries", 0),
            "taxa_acerto": stats.get("hit_rate", 0.0),
            "tamanho_mb": stats.get("size_mb", 0.0),
            "tempo_medio_ms": stats.get("avg_time_ms", 0.0),
            "recomendacao": "Cache funcionando bem" if stats.get("hit_rate", 0) > 0.5 else "Considere aumentar TTL"
        }
    except Exception as e:
        logger.error(f"Erro em cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Erro: {str(e)}")


@app.post("/advanced/cache-clear")
async def clear_cache(
    x_api_key: str = Header(None),
    request: Request = None
):
    """Limpa o cache de predições."""
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    if not ADVANCED_FEATURES or prediction_cache is None:
        raise HTTPException(
            status_code=501,
            detail="❌ Cache não disponível"
        )
    
    try:
        prediction_cache.clear()
        return {
            "mensagem": "✅ Cache limpo com sucesso",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Erro: {str(e)}")


@app.get("/advanced/system-info")
async def get_system_info(
    x_api_key: str = Header(None),
    request: Request = None
):
    """Retorna informações do sistema e features disponíveis."""
    check_api_key(x_api_key)
    check_rate_limit(request)
    
    return {
        "versao_api": "2.0.0",
        "features_avancadas": ADVANCED_FEATURES,
        "features_disponiveis": {
            "mc_dropout": ADVANCED_FEATURES,
            "drift_detection": ADVANCED_FEATURES,
            "cache_inteligente": ADVANCED_FEATURES,
            "data_augmentation": ADVANCED_FEATURES
        },
        "endpoints": {
            "basicos": ["/upload-csv", "/train", "/infer", "/metrics", "/model", "/health"],
            "avancados": [
                "/advanced/mc-dropout",
                "/advanced/check-drift",
                "/advanced/cache-stats",
                "/advanced/cache-clear",
                "/advanced/system-info"
            ]
        },
        "timestamp": datetime.now().isoformat()
    }

#!/bin/bash
set -e

echo "============================================"
echo "DEMO: Knowledge Tracing System"
echo "============================================"

# Criar e ativar venv
echo "Criando ambiente virtual..."
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretórios
mkdir -p data models results/logs results/figures uploads

# Baixar e preparar dados
echo "\nBaixando e preparando dados..."
python data/data_fetch_and_prepare.py --datasets assistments,ednet,oulad --anonymize --limit-download

# Treinar modelo
echo "\nTreinando modelo DKT (demo rápido)..."
python train_dkt.py --epochs 3 --batch-size 32 --lr 5e-4 --seed 42

# Avaliar políticas
echo "\nAvaliando políticas de recomendação..."
python evaluate_policies.py --episodes 100

# Gerar relatório
echo "\nGerando relatório..."
python utils/summary_report.py

echo "\n============================================"
echo "✅ DEMO concluído com sucesso!"
echo "============================================"
echo "Arquivos gerados:"
echo "  - data/real_combined_dataset.csv"
echo "  - models/dkt.pt"
echo "  - results/summary.json"
echo "  - results/demo_summary.txt"
echo ""
echo "Para iniciar a API:"
echo "  export SECRET_API_KEY=sua_chave"
echo "  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
echo ""
echo "Para abrir o frontend:"
echo "  cd frontend/static_demo && python -m http.server 8001"
echo "============================================"

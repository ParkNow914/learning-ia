# 🚀 Guia de Início Rápido

## Setup Completo em 5 Minutos

### 1. Clone e Entre no Diretório
```bash
git clone https://github.com/ParkNow914/learning-ia.git
cd learning-ia
```

### 2. Execute o Demo Automático
```bash
chmod +x demo_run.sh
./demo_run.sh
```

Este script faz tudo automaticamente:
- Cria ambiente virtual Python
- Instala todas as dependências
- Baixa e prepara dados educacionais
- Treina o modelo DKT (3 épocas, ~2-5 minutos)
- Avalia políticas de recomendação
- Gera relatório final

### 3. Verificar Resultados

Após a execução, você terá:

```
learning-ia/
├── data/real_combined_dataset.csv       # ~5k interações
├── models/dkt.pt                        # Modelo treinado (~291KB)
├── results/summary.json                 # Métricas (AUC, accuracy, etc.)
├── results/demo_summary.txt             # Relatório legível
└── results/figures/                     # 6 visualizações
    ├── loss.png
    ├── auc.png
    ├── auc_calibration.png
    ├── skill_gain_boxplot.png
    ├── time_to_master.png
    └── prob_heatmap.png
```

### 4. Iniciar API Local

```bash
# Ativar ambiente (se não estiver ativo)
source .venv/bin/activate

# Configurar chave de API
export SECRET_API_KEY=sua_chave_segura

# Iniciar servidor FastAPI
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API disponível em: `http://127.0.0.1:8000`

Testar:
```bash
curl http://127.0.0.1:8000/health
```

### 5. Abrir Frontend

Em outro terminal:
```bash
cd frontend/static_demo
python -m http.server 8001
```

Abra no navegador: `http://localhost:8001`

---

## Comandos Úteis

### Retreinar com mais épocas
```bash
python train_dkt.py --epochs 10 --batch-size 32
```

### Baixar mais datasets
```bash
python data/data_fetch_and_prepare.py --datasets assistments,ednet,oulad --anonymize
```

### Executar testes
```bash
pytest tests/ -v
```

### Gerar relatório atualizado
```bash
python utils/summary_report.py
```

### Converter modelo para TorchScript
```bash
python utils/convert_to_torchscript.py --model models/dkt.pt --output models/dkt_ts.pt
```

---

## Requisitos Mínimos

- Python 3.8+
- 4GB RAM
- 500MB disco
- CPU (GPU opcional)

---

## Troubleshooting Rápido

### Erro: torch não encontrado
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Erro: Permission denied em demo_run.sh
```bash
chmod +x demo_run.sh
```

### Erro: API retorna 401
```bash
# Verifique se a chave está correta
export SECRET_API_KEY=sua_chave
# E atualize em frontend/static_demo/app.js linha 2
```

---

## Próximos Passos

1. Explore o notebook: `jupyter notebook notebook_demo.ipynb`
2. Leia a documentação completa: `README.md`
3. Veja os slides de apresentação: `presentation_slides.md`
4. Check roadmap: `TODO.md`

---

## Suporte

- Issues: https://github.com/ParkNow914/learning-ia/issues
- Docs: README.md
- Tests: `pytest tests/ -v`

**Pronto! Seu sistema de Knowledge Tracing está funcionando! 🎉**

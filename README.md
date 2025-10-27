# 🎓 Knowledge Tracing + Recomendador de Exercícios

Sistema completo de **Knowledge Tracing** usando Deep Learning (DKT - LSTM) com recomendação personalizada de exercícios. Execução 100% local, sem Docker, usando dados educacionais reais.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Instalação Rápida](#instalação-rápida)
- [Uso Passo a Passo](#uso-passo-a-passo)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API REST](#api-rest)
- [Frontend](#frontend)
- [Dados e Licenças](#dados-e-licenças)
- [Troubleshooting](#troubleshooting)
- [Compliance (LGPD/GDPR)](#compliance-lgpdgdpr)

---

## 🎯 Visão Geral

Este sistema implementa:

- ✅ **Download automático** de datasets educacionais reais (Assistments, EdNet, OULAD)
- ✅ **Modelo DKT (Deep Knowledge Tracing)** com PyTorch LSTM
- ✅ **Calibração de probabilidades** (Platt Scaling / Isotonic)
- ✅ **5 estratégias de recomendação**: target, info_gain, exploration, heuristic, random
- ✅ **API REST local** (FastAPI) com autenticação e rate limiting
- ✅ **Frontend profissional** (HTML/CSS/JS vanilla + Chart.js)
- ✅ **Detecção de drift** (KS-test) e fallback heurístico
- ✅ **Testes automatizados** (pytest) e CI/CD (GitHub Actions)
- ✅ **Conversão para TorchScript/ONNX** para produção

### Características Principais

- 🚫 **Sem Docker**: tudo roda localmente com venv
- 📊 **Dados reais**: apenas datasets públicos com licenças validadas
- 🔒 **Segurança**: anonimização com hash salted, API key, rate limiting
- 🎲 **Reproducível**: seed fixa (42) em todo o pipeline
- 📈 **Visualizações**: gráficos de calibração, skill gain, time-to-master

---

## 💻 Requisitos

- **Python 3.8+**
- **CPU** (GPU opcional, mas não necessário)
- **4GB RAM** mínimo
- **500MB espaço em disco**

### Dependências Principais

```
torch>=1.12.0
numpy, pandas, scikit-learn
matplotlib, seaborn
fastapi, uvicorn
pytest
```

Veja `requirements.txt` completo para versões fixas.

---

## ⚡ Instalação Rápida

### Opção 1: Script Demo Automático (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/ParkNow914/learning-ia.git
cd learning-ia

# Execute o demo completo
chmod +x demo_run.sh
./demo_run.sh
```

Este script:
1. Cria e ativa ambiente virtual
2. Instala todas as dependências
3. Baixa e prepara dados
4. Treina o modelo (3 épocas, ~5 min)
5. Avalia políticas
6. Gera relatório final

### Opção 2: Instalação Manual

```bash
# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite .env e altere SECRET_API_KEY e SALT_ANON
```

---

## 📚 Uso Passo a Passo

### 1. Baixar e Preparar Dados

```bash
python data/data_fetch_and_prepare.py \
    --datasets assistments,ednet,oulad \
    --anonymize \
    --seed 42
```

**Saídas:**
- `data/real_combined_dataset.csv` - Dataset unificado
- `data/sources.json` - Metadados das fontes
- `results/stats.json` - Estatísticas dos dados

**Exemplo das primeiras linhas do dataset:**

```csv
student_id,timestamp,item_id,skill_id,correct,ability_truth,source
a1b2c3d4e5f6,2009-09-01T00:00:00,item_0,3,1,0.456,assistments
a1b2c3d4e5f6,2009-09-02T00:00:00,item_12,7,0,0.456,assistments
f9e8d7c6b5a4,2019-01-01T00:00:00,ednet_item_23,15,1,-0.123,ednet
```

### 2. Treinar Modelo DKT

```bash
python train_dkt.py \
    --epochs 5 \
    --batch-size 32 \
    --lr 5e-4 \
    --hidden-size 128 \
    --seed 42
```

**Parâmetros:**
- `--epochs`: Número de épocas (padrão: 5, use 3 para demo rápido)
- `--batch-size`: Tamanho do batch
- `--lr`: Learning rate
- `--hidden-size`: Dimensão da camada oculta LSTM
- `--n-layers`: Número de camadas LSTM (padrão: 2)
- `--max-seq-len`: Comprimento máximo da sequência (padrão: 200)

**Saídas:**
- `models/dkt.pt` - Modelo treinado
- `models/metadata.json` - Metadados do modelo
- `results/train_log.csv` - Log de treino
- `results/figures/loss.png` - Gráfico de loss
- `results/figures/auc.png` - Gráfico de AUC

### 3. Avaliar Políticas de Recomendação

```bash
python evaluate_policies.py --episodes 100
```

**Saídas:**
- `results/summary.json` - Métricas completas
- `results/episodes_log.csv` - Log detalhado
- `results/figures/` - 4 visualizações obrigatórias:
  - `auc_calibration.png` - Calibração do modelo
  - `skill_gain_boxplot.png` - Ganho de habilidade por política
  - `time_to_master.png` - Tempo até maestria
  - `prob_heatmap.png` - Heatmap de probabilidades

### 4. Iniciar API Local

```bash
# Configurar API key
export SECRET_API_KEY=sua_chave_segura_aqui

# Iniciar servidor
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API estará disponível em `http://127.0.0.1:8000`

**Endpoints principais:**
- `POST /upload-csv` - Upload de dados
- `POST /train` - Treinar modelo
- `POST /infer` - Obter recomendação
- `GET /metrics` - Ver métricas
- `GET /model` - Download do modelo
- `GET /health` - Health check

### 5. Abrir Frontend

```bash
# Navegar para o diretório frontend
cd frontend/static_demo

# Servir arquivos estáticos
python -m http.server 8001
```

Abra `http://localhost:8001` no navegador.

---

## 📁 Estrutura do Projeto

```
learning-ia/
├── data/
│   ├── data_fetch_and_prepare.py    # Download e preparação de dados
│   ├── real_combined_dataset.csv    # Dataset unificado (gerado)
│   └── sources.json                 # Metadados das fontes (gerado)
│
├── models/
│   ├── dkt.pt                       # Modelo treinado (gerado)
│   ├── metadata.json                # Metadados do modelo (gerado)
│   ├── calibrator.pkl               # Calibrador de probabilidades (gerado)
│   └── best_params.json             # Melhores hiperparâmetros (gerado)
│
├── results/
│   ├── summary.json                 # Métricas consolidadas
│   ├── stats.json                   # Estatísticas dos dados
│   ├── demo_summary.txt             # Relatório legível
│   ├── logs/                        # Logs estruturados (JSON-lines)
│   └── figures/                     # Visualizações
│
├── app/
│   └── main.py                      # API FastAPI
│
├── frontend/static_demo/
│   ├── index.html                   # Frontend principal
│   ├── app.js                       # Lógica JavaScript
│   ├── style.css                    # Estilos CSS
│   └── design_tokens.json           # Tokens de design
│
├── utils/
│   ├── calibration.py               # Calibração de probabilidades
│   ├── hyperparam_search.py         # Busca de hiperparâmetros
│   ├── convert_to_torchscript.py    # Conversão para TorchScript
│   └── summary_report.py            # Geração de relatórios
│
├── scripts/
│   └── prepare_real_data.py         # Preparação de dados customizados
│
├── tests/
│   ├── test_data_fetch.py           # Testes de dados
│   ├── test_dkt.py                  # Testes do modelo
│   └── test_recommender.py          # Testes do recomendador
│
├── dkt_model.py                     # Definição do modelo DKT
├── train_dkt.py                     # Script de treino
├── recommender.py                   # Sistema de recomendação
├── evaluate_policies.py             # Avaliação de políticas
├── demo_run.sh                      # Script demo completo
├── requirements.txt                 # Dependências Python
├── .env.example                     # Exemplo de configuração
├── .gitignore                       # Arquivos ignorados
└── README.md                        # Este arquivo
```

---

## 🔌 API REST

### Autenticação

Todas as rotas (exceto `/health`) requerem header `x-api-key`:

```bash
curl -H "x-api-key: sua_chave" http://127.0.0.1:8000/metrics
```

Configure a chave em `.env`:
```
SECRET_API_KEY=sua_chave_segura_aqui
```

### Rate Limiting

- **60 requisições por minuto** por IP (configurável via `RATE_LIMIT_PER_MIN`)
- Implementação in-memory (para produção, use Redis)

### Exemplos de Uso

#### Upload de CSV

```bash
curl -X POST \
  -H "x-api-key: sua_chave" \
  -F "file=@data/real_combined_dataset.csv" \
  http://127.0.0.1:8000/upload-csv
```

**Resposta:**
```json
{
  "n_students": 680,
  "n_items": 150,
  "sample_rows": [...]
}
```

#### Obter Recomendação

```bash
curl -X POST \
  -H "x-api-key: sua_chave" \
  -H "Content-Type: application/json" \
  -d '{
    "student_history": [
      {"item_id": "item_1", "correct": 1},
      {"item_id": "item_5", "correct": 0}
    ],
    "candidate_items": ["item_3", "item_7", "item_12"],
    "strategy": "target",
    "target_p": 0.7
  }' \
  http://127.0.0.1:8000/infer
```

**Resposta:**
```json
{
  "item_id": "item_7",
  "p_estimated": 0.698,
  "p_raw": 0.701,
  "rationale": "Item com P(correct) mais próxima de 0.70",
  "strategy": "target",
  "candidates": [...]
}
```

---

## 📊 Dados e Licenças

### Datasets Suportados

| Dataset | Licença | URL | Descrição |
|---------|---------|-----|-----------|
| **ASSISTments 2009-2010** | CC BY 4.0 | [Link](https://sites.google.com/site/assistmentsdata/datasets) | Sistema de tutoria inteligente |
| **EdNet KT1** | CC BY-NC 4.0 | [Link](https://github.com/riiid/ednet) | Plataforma de aprendizado online |
| **OULAD** | CC BY 4.0 | [Link](https://analyse.kmi.open.ac.uk/open_dataset) | Open University Learning Analytics |

### Schema Canônico

Todos os dados são normalizados para:

```csv
student_id,timestamp,item_id,skill_id,correct,ability_truth,source
```

---

## 🔧 Troubleshooting

### Problema: Erro ao instalar PyTorch

**Solução:**
```bash
# CPU only
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Problema: API retorna 401 Unauthorized

**Solução:**
Verifique se a chave está correta:
```bash
export SECRET_API_KEY=sua_chave
# Deve ser a mesma em .env e nas requisições
```

---

## 🔒 Compliance (LGPD/GDPR)

### Anonimização

Por padrão, todos os `student_id` são anonimizados via hash SHA256 com salt configurável em `.env`.

⚠️ **IMPORTANTE**: Nunca versione o `.env` com o salt real.

### Aviso Legal

⚠️ **Este sistema é para fins educacionais e de pesquisa.**

Não use para decisões de alto impacto sem validação humana e auditoria de viés.

---

**🎉 Pronto para começar! Execute `./demo_run.sh` e veja a mágica acontecer!**
# 🚀 API Avançada - Knowledge Tracing

Documentação completa dos endpoints avançados da API de Knowledge Tracing.

## 📋 Índice

1. [Configuração Inicial](#configuração-inicial)
2. [Autenticação](#autenticação)
3. [Endpoints Básicos](#endpoints-básicos)
4. [Endpoints Avançados](#endpoints-avançados)
5. [Exemplos de Uso](#exemplos-de-uso)
6. [Códigos de Erro](#códigos-de-erro)

---

## 🔧 Configuração Inicial

### Iniciar API

```bash
# Ativar ambiente virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows

# Iniciar servidor
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

A API estará disponível em: `http://127.0.0.1:8000`

### Documentação Interativa

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## 🔐 Autenticação

Todos os endpoints (exceto `/health`) requerem autenticação via header `x-api-key`.

```bash
# Configurar chave (arquivo .env)
SECRET_API_KEY=sua_chave_super_secreta_123
```

### Exemplo de Request

```bash
curl -X POST http://127.0.0.1:8000/infer \
  -H "x-api-key: sua_chave_super_secreta_123" \
  -H "Content-Type: application/json" \
  -d '{"student_history": [...], "candidate_items": [...]}'
```

---

## 📡 Endpoints Básicos

### 1. Health Check

Verifica se a API está operacional.

**Endpoint**: `GET /health`

**Autenticação**: ❌ Não requer

```bash
curl http://127.0.0.1:8000/health
```

**Resposta**:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 2. Upload de CSV

Envia dados de estudantes para o sistema.

**Endpoint**: `POST /upload-csv`

**Autenticação**: ✅ Requer

**Formato do CSV**:
```csv
student_id,timestamp,item_id,skill_id,correct,ability_truth,source
aluno_01,2024-01-15T10:00:00Z,ex_mat_01,skill_algebra,1,0.75,manual
```

**Exemplo**:
```bash
curl -X POST http://127.0.0.1:8000/upload-csv \
  -H "x-api-key: sua_chave" \
  -F "file=@dados_alunos.csv"
```

**Resposta**:
```json
{
  "mensagem": "✅ Arquivo carregado com sucesso!",
  "n_estudantes": 100,
  "n_exercicios": 245,
  "n_interacoes": 5659,
  "exemplo": [
    {"aluno": "hash_abc", "exercicio": "ex_01", "correto": 1}
  ]
}
```

---

### 3. Treinar Modelo

Inicia o treinamento do modelo DKT.

**Endpoint**: `POST /train`

**Body**:
```json
{
  "epochs": 5,
  "batch_size": 32,
  "learning_rate": 0.0005,
  "hidden_size": 128
}
```

**Exemplo**:
```bash
curl -X POST http://127.0.0.1:8000/train \
  -H "x-api-key: sua_chave" \
  -H "Content-Type: application/json" \
  -d '{"epochs": 5, "batch_size": 32}'
```

**Resposta**:
```json
{
  "status": "✅ Treinamento concluído",
  "melhor_epoca": 3,
  "auc_validacao": 0.602,
  "acuracia": 0.781,
  "perda_final": 0.489,
  "duracao_segundos": 45.3,
  "modelo_salvo": "models/dkt.pt"
}
```

---

### 4. Obter Recomendação

Recomenda o próximo exercício para um aluno.

**Endpoint**: `POST /infer`

**Body**:
```json
{
  "student_history": [
    {"item_id": "ex_01", "correct": 1, "timestamp": "2024-01-15T10:00:00Z"},
    {"item_id": "ex_02", "correct": 0, "timestamp": "2024-01-15T10:05:00Z"}
  ],
  "candidate_items": ["ex_03", "ex_04", "ex_05"],
  "strategy": "target",
  "target_p": 0.7
}
```

**Estratégias Disponíveis**:
- `target`: Dificuldade ideal (P=0.7) - **RECOMENDADO** 🌟
- `info_gain`: Máximo ganho de informação
- `exploration`: Máxima incerteza
- `heuristic`: Heurística simples (fallback)
- `random`: Aleatório (baseline)

**Resposta**:
```json
{
  "item_recomendado": "ex_mat_07",
  "probabilidade_acerto": 0.698,
  "estrategia_usada": "target",
  "justificativa": "🎯 Item com dificuldade ideal (70%) para aprendizado ótimo",
  "todos_candidatos": [
    {
      "item": "ex_mat_07",
      "prob_bruta": 0.682,
      "prob_calibrada": 0.698,
      "classificacao": 1
    }
  ],
  "confianca": "alta"
}
```

---

### 5. Obter Métricas

Retorna métricas de avaliação do modelo.

**Endpoint**: `GET /metrics`

**Resposta**:
```json
{
  "auc_dkt": 0.850,
  "accuracy_dkt": 0.780,
  "avg_gain_dkt": 0.152,
  "time_to_master_mean_dkt": 15.5,
  "calibration_bins": [...],
  "n_students_simulated": 100,
  "model_version": "v1.0.0"
}
```

---

### 6. Download do Modelo

Baixa o arquivo do modelo treinado.

**Endpoint**: `GET /model`

**Exemplo**:
```bash
curl -X GET http://127.0.0.1:8000/model \
  -H "x-api-key: sua_chave" \
  -o modelo_dkt.pt
```

---

## ✨ Endpoints Avançados

### 1. MC Dropout - Estimativa de Incerteza

Usa MC Dropout para estimar a confiança da predição.

**Endpoint**: `POST /advanced/mc-dropout`

**Body**:
```json
{
  "student_history": [...],
  "candidate_item": "ex_07",
  "n_samples": 10
}
```

**Resposta**:
```json
{
  "mensagem": "✅ MC Dropout inference executado",
  "probabilidade_media": 0.72,
  "incerteza_std": 0.04,
  "confianca": "alta",
  "n_samples": 10,
  "dica": "Incerteza baixa indica alta confiança na predição"
}
```

**Interpretação**:
- `incerteza_std < 0.05`: Alta confiança ✅
- `0.05 < incerteza_std < 0.10`: Média confiança ⚠️
- `incerteza_std > 0.10`: Baixa confiança ❌

---

### 2. Detecção de Drift

Verifica se há mudanças significativas na distribuição dos dados.

**Endpoint**: `POST /advanced/check-drift`

**Body**: Multipart form com arquivo CSV

**Exemplo**:
```bash
curl -X POST http://127.0.0.1:8000/advanced/check-drift \
  -H "x-api-key: sua_chave" \
  -F "file=@novos_dados.csv"
```

**Resposta**:
```json
{
  "mensagem": "✅ Análise de drift concluída",
  "drift_detectado": false,
  "psi_score": 0.08,
  "ks_statistic": 0.12,
  "recomendacao": "Nenhuma ação necessária",
  "detalhes": {
    "feature_drifts": [...],
    "concept_drift": false
  }
}
```

**Interpretação PSI**:
- `PSI < 0.1`: Sem drift significativo ✅
- `0.1 < PSI < 0.25`: Drift moderado ⚠️
- `PSI > 0.25`: Drift severo - retreinar modelo ❌

---

### 3. Estatísticas do Cache

Retorna informações sobre o cache de predições.

**Endpoint**: `GET /advanced/cache-stats`

**Resposta**:
```json
{
  "mensagem": "✅ Estatísticas do cache",
  "entradas_totais": 1247,
  "taxa_acerto": 0.87,
  "tamanho_mb": 2.3,
  "tempo_medio_ms": 0.8,
  "recomendacao": "Cache funcionando bem"
}
```

---

### 4. Limpar Cache

Remove todas as entradas do cache.

**Endpoint**: `POST /advanced/cache-clear`

**Resposta**:
```json
{
  "mensagem": "✅ Cache limpo com sucesso",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 5. Informações do Sistema

Lista todas as features e endpoints disponíveis.

**Endpoint**: `GET /advanced/system-info`

**Resposta**:
```json
{
  "versao_api": "2.0.0",
  "features_avancadas": true,
  "features_disponiveis": {
    "mc_dropout": true,
    "drift_detection": true,
    "cache_inteligente": true,
    "data_augmentation": true
  },
  "endpoints": {
    "basicos": ["/upload-csv", "/train", "/infer", ...],
    "avancados": ["/advanced/mc-dropout", "/advanced/check-drift", ...]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 💻 Exemplos de Uso Completos

### Exemplo 1: Fluxo Básico Completo

```python
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"
API_KEY = "sua_chave_super_secreta_123"
headers = {"x-api-key": API_KEY}

# 1. Verificar saúde
response = requests.get(f"{API_URL}/health")
print(response.json())

# 2. Upload de dados
with open("dados_alunos.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{API_URL}/upload-csv", headers=headers, files=files)
    print(response.json())

# 3. Treinar modelo
train_config = {"epochs": 5, "batch_size": 32}
response = requests.post(f"{API_URL}/train", headers=headers, json=train_config)
print(response.json())

# 4. Obter recomendação
infer_data = {
    "student_history": [
        {"item_id": "ex_01", "correct": 1, "timestamp": "2024-01-15T10:00:00Z"}
    ],
    "candidate_items": ["ex_02", "ex_03"],
    "strategy": "target"
}
response = requests.post(f"{API_URL}/infer", headers=headers, json=infer_data)
print(response.json())

# 5. Obter métricas
response = requests.get(f"{API_URL}/metrics", headers=headers)
print(response.json())
```

---

### Exemplo 2: Usando Features Avançadas

```python
# 1. Verificar features disponíveis
response = requests.get(f"{API_URL}/advanced/system-info", headers=headers)
print(response.json())

# 2. MC Dropout para incerteza
mc_data = {
    "student_history": [...],
    "candidate_item": "ex_07",
    "n_samples": 20
}
response = requests.post(f"{API_URL}/advanced/mc-dropout", headers=headers, json=mc_data)
result = response.json()
print(f"Probabilidade: {result['probabilidade_media']:.2%} ± {result['incerteza_std']:.2%}")

# 3. Verificar drift nos dados
with open("novos_dados.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{API_URL}/advanced/check-drift", headers=headers, files=files)
    drift_result = response.json()
    if drift_result["drift_detectado"]:
        print("⚠️ ALERTA: Drift detectado! Considere retreinar o modelo.")
    else:
        print("✅ Sem drift significativo")

# 4. Estatísticas do cache
response = requests.get(f"{API_URL}/advanced/cache-stats", headers=headers)
cache_stats = response.json()
print(f"Taxa de acerto do cache: {cache_stats['taxa_acerto']:.1%}")
print(f"Speedup médio: {cache_stats['tempo_medio_ms']:.2f}ms")
```

---

## ⚠️ Códigos de Erro

| Código | Significado | Solução |
|--------|-------------|---------|
| **200** | ✅ Sucesso | - |
| **401** | 🔒 Não autorizado | Verificar `x-api-key` no header |
| **404** | 📂 Não encontrado | Verificar se modelo/dados existem |
| **429** | 🚦 Rate limit excedido | Aguardar 1 minuto |
| **500** | ❌ Erro interno | Verificar logs em `results/logs/api.log` |
| **501** | 🚧 Não implementado | Feature avançada indisponível |

---

## 📊 Rate Limiting

- **Limite padrão**: 60 requisições por minuto por IP
- **Configuração**: Variável `RATE_LIMIT_PER_MIN` no `.env`

```bash
# .env
RATE_LIMIT_PER_MIN=120  # Aumentar para 120 req/min
```

---

## 🔧 Troubleshooting

### Erro: "Features avançadas não disponíveis"

**Causa**: Dependências não instaladas

**Solução**:
```bash
pip install scipy
```

### Erro: "Invalid API key"

**Causa**: Chave incorreta ou não configurada

**Solução**:
```bash
# .env
SECRET_API_KEY=sua_chave_aqui
```

### Erro: "Rate limit exceeded"

**Causa**: Muitas requisições em curto período

**Solução**: Aguardar 60 segundos ou aumentar limite no `.env`

---

## 📚 Recursos Adicionais

- **Documentação Geral**: README.md
- **Guia para Iniciantes**: GUIA_INICIANTES.md
- **Documentação Didática**: README_DIDATICO.md
- **Melhorias Implementadas**: IMPROVEMENTS.md

---

## 🤝 Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `results/logs/api.log`
2. Consulte a documentação interativa: http://127.0.0.1:8000/docs
3. Execute o validador: `python validar_sistema.py`

---

**🇧🇷 Sistema 100% em Português BR**

Democratizando IA Educacional no Brasil! ✨

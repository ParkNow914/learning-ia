# 🏗️ Documentação de Arquitetura do Sistema

## Visão Geral

O sistema Knowledge Tracing + Recomendador de Exercícios é uma solução completa de Inteligência Artificial para educação personalizada. Esta documentação descreve a arquitetura do sistema, componentes principais, fluxos de dados e decisões de design.

## 📊 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                    │
├─────────────────────────────────────────────────────────────┤
│  Frontend Demo       │  Dashboard Admin   │   Notebook      │
│  (HTML/CSS/JS)       │  (HTML/CSS/JS)     │   (Jupyter)     │
└────────┬─────────────┴──────────┬──────────┴────────┬────────┘
         │                        │                    │
         └────────────────┬───────┴────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                    CAMADA DE API (FastAPI)                 │
├────────────────────────────────────────────────────────────┤
│  Endpoints Básicos:                                        │
│  - /upload-csv    - /train      - /infer                  │
│  - /metrics       - /model      - /health                 │
│                                                            │
│  Endpoints Avançados:                                      │
│  - /advanced/mc-dropout      - /advanced/check-drift      │
│  - /advanced/cache-stats     - /advanced/cache-clear      │
│  - /advanced/system-info                                   │
│                                                            │
│  Middleware: CORS, Rate Limiting, Autenticação             │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────┐
│                  CAMADA DE LÓGICA DE NEGÓCIO               │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Recommender  │  │  Evaluator   │  │  Calibrator  │    │
│  │   Engine     │  │   Policies   │  │   (Platt)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Drift      │  │     Cache    │  │ Performance  │    │
│  │  Detector    │  │  Optimizer   │  │   Monitor    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                            │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────┐
│                   CAMADA DE MODELO (ML)                    │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌────────────────────────────────────────────────┐       │
│  │         DKT Model (PyTorch LSTM)               │       │
│  │  - Input: Sequence of (item, response)        │       │
│  │  - Output: P(correct | history)               │       │
│  │  - Architecture: Embedding → LSTM → Linear    │       │
│  └────────────────────────────────────────────────┘       │
│                                                            │
│  ┌────────────────────────────────────────────────┐       │
│  │      DKT Advanced (MC Dropout, GRU, Ensemble)  │       │
│  │  - Uncertainty Estimation (MC Dropout)         │       │
│  │  - Alternative RNN (GRU support)               │       │
│  │  - Ensemble predictions                        │       │
│  └────────────────────────────────────────────────┘       │
│                                                            │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────┐
│                   CAMADA DE DADOS                          │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Real Data   │  │   Augmented  │  │   Features   │    │
│  │   Fetcher    │  │     Data     │  │  Engineering │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                            │
│  Datasets: Assistments, EdNet, OULAD                      │
│  Schema: student_id, timestamp, item_id, skill_id,        │
│          correct, ability_truth, source                    │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

## 🧩 Componentes Principais

### 1. Camada de Apresentação

#### Frontend Demo (`frontend/static_demo/`)
- **Tecnologia**: HTML5, CSS3, Vanilla JavaScript, Chart.js
- **Features**:
  - Upload de dados CSV
  - Visualização de histórico de alunos
  - Solicitação de recomendações
  - Gráficos de performance
  - Modo Dark/Light
- **Design**: Responsivo, WCAG AA, CSS Variables

#### Dashboard Administrativo (`frontend/admin_dashboard.html`)
- **Tecnologia**: HTML5, CSS3, JavaScript
- **Features**:
  - Métricas em tempo real
  - Monitoramento de cache
  - Detecção de drift
  - Logs estruturados
  - Controles administrativos
- **Auto-refresh**: 30 segundos

#### Notebook Demo (`notebook_demo.ipynb`)
- **Tecnologia**: Jupyter Notebook
- **Conteúdo**:
  - EDA (Exploratory Data Analysis)
  - Treinamento de modelo
  - Demonstração de recomendações
  - Visualizações interativas

### 2. Camada de API

#### FastAPI Application (`app/main.py`)
- **Versão**: 2.0.0
- **Autenticação**: API Key (header `x-api-key`)
- **Rate Limiting**: 60 requisições/minuto por IP (in-memory)
- **CORS**: Configurado para permitir cross-origin

**Endpoints Básicos**:
- `POST /upload-csv`: Upload e validação de CSV
- `POST /train`: Treinar/fine-tune modelo
- `POST /infer`: Obter recomendação
- `GET /metrics`: Buscar métricas do modelo
- `GET /model`: Download do modelo treinado
- `GET /health`: Health check

**Endpoints Avançados**:
- `POST /advanced/mc-dropout`: Inferência com MC Dropout
- `POST /advanced/check-drift`: Detectar drift em novos dados
- `GET /advanced/cache-stats`: Estatísticas do cache
- `POST /advanced/cache-clear`: Limpar cache
- `GET /advanced/system-info`: Informações do sistema

**Middleware**:
- CORS (Cross-Origin Resource Sharing)
- Rate Limiting (in-memory)
- Logging estruturado (JSON-lines)
- Error handling com mensagens amigáveis

### 3. Camada de Lógica de Negócio

#### Recommender Engine (`recommender.py`)
- **Estratégias**:
  1. **Target**: Zona de desenvolvimento proximal (P=0.7)
  2. **Info Gain**: Maximiza ganho de informação
  3. **Exploration**: Maximiza incerteza (exploração)
  4. **Heuristic**: Fallback heurístico
  5. **Random**: Baseline aleatório
- **Output**: Item recomendado + probabilidade + justificativa

#### Policy Evaluator (`evaluate_policies.py`)
- Simula episódios de aprendizado
- Compara estratégias de recomendação
- Gera métricas: AUC, Accuracy, Ganho, Time-to-Mastery
- Produz 6 visualizações
- Salva `results/summary.json`

#### Calibrator (`utils/calibration.py`)
- **Métodos**: Platt Scaling, Isotonic Regression
- **Input**: Probabilidades não calibradas
- **Output**: Probabilidades calibradas
- **Persistência**: `models/calibrator.pkl`

#### Drift Detector (`utils/drift_detection.py`)
- **Testes**:
  - KS-test (Kolmogorov-Smirnov) para features
  - PSI (Population Stability Index)
  - Concept drift (queda de accuracy)
- **Alertas**: Automáticos quando drift > threshold
- **Logging**: `results/alerts.log`

#### Cache Optimizer (`utils/optimization.py`)
- **Cache de Predições**:
  - TTL configurável
  - Eviction automática (LRU)
  - Hit rate tracking
- **Batch Inference**: Otimizado para múltiplas predições
- **Speedup**: 90%+ para queries repetidas

#### Performance Monitor (`utils/performance_monitor.py`)
- **Métricas**:
  - Latência (avg, p50, p95, p99, max)
  - Throughput (predições/minuto)
  - Taxa de erro
  - Uptime
- **Alertas**: Automáticos por threshold
- **Relatórios**: Formatados e salvos em JSON

### 4. Camada de Modelo

#### DKT Model (`dkt_model.py`)
- **Arquitetura**:
  ```
  Input: (item_id, correct) → [batch, seq_len, 2]
  Embedding: 2N → emb_dim (N items, cada um com 2 estados)
  LSTM: [batch, seq_len, emb_dim] → [batch, seq_len, hidden_size]
  Linear: hidden_size → 1
  Output: P(correct | history)
  ```
- **Configurável**:
  - `n_items`: Número de exercícios
  - `hidden_size`: Tamanho do LSTM (default: 128)
  - `n_layers`: Camadas do LSTM (default: 2)
  - `dropout`: Dropout rate (default: 0.2)

#### DKT Advanced (`dkt_model_advanced.py`)
- **MC Dropout**: Estimativa de incerteza com múltiplas amostras
- **GRU Support**: Alternativa ao LSTM
- **Ensemble**: Combina múltiplos modelos
- **Predict with Uncertainty**: Retorna mean ± std

#### Trainer (`train_dkt.py`)
- **Otimizador**: AdamW
- **Loss**: BCEWithLogitsLoss
- **Scheduler**: ReduceLROnPlateau
- **Early Stopping**: Baseado em val_loss
- **Logging**: `results/train_log.csv`
- **Checkpoints**: Melhor modelo salvo
- **Visualizações**: Loss e AUC curves

### 5. Camada de Dados

#### Data Fetcher (`data/data_fetch_and_prepare.py`)
- **Datasets Suportados**:
  - **Assistments**: Matemática K-12 (CC BY 4.0)
  - **EdNet**: MOOC clickstream (CC BY-NC 4.0)
  - **OULAD**: Open University (CC BY 4.0)
- **Pipeline**:
  1. Download automático
  2. Validação de licença
  3. Normalização para schema canônico
  4. Anonimização (SHA256 salted)
  5. Salvar CSV + metadata JSON
- **Output**:
  - `data/real_combined_dataset.csv`
  - `data/sources.json`

#### Data Augmentor (`utils/data_augmentation.py`)
- **Métodos**:
  - **Sliding Window**: Cria sequências sobrepostas
  - **Perturbation**: Adiciona ruído controlado
  - **Synthetic Students**: Gera alunos baseados em IRT
- **Feature Engineering**:
  - Temporais: time_since_last, streaks
  - Agregadas: accuracy histórica, dificuldade
  - Habilidades: performance por skill

## 🔄 Fluxos de Dados

### Fluxo de Treino

```
1. Data Fetch
   ├─ Download datasets públicos
   ├─ Validar licenças
   ├─ Normalizar para schema
   ├─ Anonimizar estudantes
   └─ Salvar CSV + metadata
   
2. Data Augmentation (opcional)
   ├─ Sliding window
   ├─ Perturbation
   └─ Feature engineering
   
3. Build Dataset
   ├─ Agrupar por aluno
   ├─ Ordenar por timestamp
   ├─ Criar sequências
   ├─ Pad/truncate para max_seq_len
   └─ Split train/val/test
   
4. Train Model
   ├─ Forward pass (LSTM)
   ├─ Compute loss (BCE)
   ├─ Backward pass
   ├─ Update weights (AdamW)
   ├─ Validate epoch
   ├─ Scheduler step
   └─ Early stopping check
   
5. Calibrate Probabilities
   ├─ Obter predições em validation set
   ├─ Fit calibrator (Platt/Isotonic)
   └─ Salvar calibrator
   
6. Evaluate
   ├─ Simular episódios
   ├─ Comparar políticas
   ├─ Calcular métricas
   └─ Gerar visualizações
   
7. Save Artifacts
   ├─ models/dkt.pt
   ├─ models/metadata.json
   ├─ models/calibrator.pkl
   └─ results/summary.json
```

### Fluxo de Inferência

```
1. API Request
   ├─ POST /infer
   ├─ Headers: x-api-key
   └─ Body: {student_history, candidate_items, strategy, target_p}
   
2. Autenticação
   ├─ Validar API key
   └─ Check rate limit
   
3. Load Model
   ├─ Carregar models/dkt.pt
   └─ Carregar models/calibrator.pkl
   
4. Check Cache (opcional)
   ├─ Gerar cache key
   ├─ Verificar se existe
   └─ Retornar se hit
   
5. Preprocess
   ├─ Converter histórico para tensors
   ├─ Mapear items para índices
   └─ Pad para max_seq_len
   
6. Predict
   ├─ Forward pass do modelo
   ├─ Aplicar calibration
   └─ Para cada candidato: obter P(correct)
   
7. Recommend
   ├─ Aplicar estratégia (target/info_gain/etc)
   ├─ Ranquear candidatos
   ├─ Selecionar melhor item
   └─ Gerar justificativa
   
8. Cache Result (opcional)
   └─ Salvar no cache com TTL
   
9. Monitor Performance
   ├─ Registrar latência
   ├─ Incrementar contador
   └─ Check thresholds
   
10. API Response
    └─ JSON: {item_id, p_estimated, rationale, candidates}
```

### Fluxo de Monitoramento

```
1. Performance Monitor
   ├─ Registrar cada predição
   │  ├─ Latência
   │  ├─ Success/failure
   │  └─ Metadata
   ├─ Calcular métricas agregadas
   │  ├─ Latência média, p95, p99
   │  ├─ Throughput
   │  └─ Taxa de erro
   └─ Alertar se threshold ultrapassado
   
2. Drift Detection
   ├─ Comparar distribuições
   │  ├─ KS-test por feature
   │  ├─ PSI score
   │  └─ Concept drift (accuracy)
   ├─ Detectar mudanças significativas
   └─ Logar alertas
   
3. Cache Management
   ├─ Monitorar hit rate
   ├─ Verificar tamanho
   ├─ Evict entradas expiradas
   └─ Reportar estatísticas
   
4. Logging
   ├─ JSON-lines estruturado
   ├─ Timestamp UTC
   ├─ Level (INFO/WARNING/ERROR)
   └─ Metadata contextual
```

## 🎯 Decisões de Design

### Por que LSTM para DKT?
- **Sequencial**: Alunos aprendem sequencialmente
- **Memória de longo prazo**: LSTM captura dependências temporais
- **Estado oculto**: Representa conhecimento latente do aluno
- **Proven**: Baseline estabelecido na literatura de KT

### Por que FastAPI?
- **Performance**: Assíncrono, rápido
- **Type hints**: Validação automática com Pydantic
- **Docs automáticas**: OpenAPI/Swagger gerado
- **Moderno**: Python 3.8+, async/await

### Por que Não Docker?
- **Requisito**: Execução local sem Docker
- **Acessibilidade**: Mais simples para leigos
- **Virtualenv**: Isolamento suficiente
- **Portabilidade**: Funciona em Win/Mac/Linux

### Por que Cache In-Memory?
- **Simplicidade**: Sem dependências externas (Redis)
- **Performance**: Acesso instantâneo
- **Local-first**: Funciona offline
- **Trade-off**: Não persiste após restart (aceitável)

### Por que MC Dropout para Incerteza?
- **Simplicidade**: Fácil de implementar
- **Eficiência**: Rápido em CPU
- **Bayesian approximation**: Aproximação válida
- **Prático**: Funciona bem na prática

## 📊 Métricas e Monitoramento

### Métricas do Modelo
- **AUC**: Area Under ROC Curve (principal)
- **Accuracy**: Taxa de acerto
- **Calibration**: ECE (Expected Calibration Error)
- **Loss**: Binary Cross-Entropy

### Métricas de Recomendação
- **Avg Gain**: Ganho médio de habilidade
- **Time to Mastery**: Tempo até dominar skill
- **Coverage**: % de itens recomendados

### Métricas de Performance
- **Latência**: p50, p95, p99 em ms
- **Throughput**: Predições/minuto
- **Error Rate**: % de falhas
- **Cache Hit Rate**: % de cache hits

### Métricas de Drift
- **PSI Score**: Population Stability Index
- **KS Statistic**: Kolmogorov-Smirnov
- **Accuracy Drop**: Δ accuracy entre baseline e current

## 🔒 Segurança e Privacidade

### Anonimização
- **Método**: SHA256 salted hash
- **Salt**: Configurável via .env (SALT_ANON)
- **Irreversível**: Não permite de-anonimização

### Autenticação
- **Método**: API Key (header x-api-key)
- **Storage**: .env (não versionado)
- **Geração**: Token seguro aleatório

### Rate Limiting
- **Limite**: 60 req/min por IP (configurável)
- **Método**: In-memory counter
- **Response**: 429 Too Many Requests

### LGPD/GDPR Compliance
- **Consentimento**: Dados públicos educacionais
- **Minimização**: Apenas dados necessários
- **Anonimização**: Hash irreversível
- **Direito ao esquecimento**: Remove dados de alunos

## 🚀 Escalabilidade

### Limitações Atuais
- **Cache in-memory**: Não escalável entre instâncias
- **Rate limiting in-memory**: Não compartilhado
- **Single-instance**: Sem load balancing

### Futuras Melhorias
- **Redis**: Para cache distribuído
- **PostgreSQL**: Para persistência de métricas
- **Load balancer**: Nginx/HAProxy
- **Containerização**: Docker opcional
- **Kubernetes**: Para orquestração

## 🧪 Testes

### Tipos de Testes
1. **Unit tests**: Funções individuais
2. **Integration tests**: Fluxos completos
3. **API tests**: Endpoints FastAPI
4. **Performance tests**: Latência e throughput

### Cobertura
- **Alvo**: > 85%
- **Atual**: ~85%
- **Ferramenta**: pytest-cov

## 📚 Referências

### Papers
- Deep Knowledge Tracing (Piech et al., 2015)
- Self-Attentive Knowledge Tracing (Pandey & Karypis, 2019)
- Calibration in Neural Networks (Guo et al., 2017)

### Datasets
- Assistments (CC BY 4.0)
- EdNet (CC BY-NC 4.0)
- OULAD (CC BY 4.0)

### Frameworks
- PyTorch 1.12+
- FastAPI 0.95+
- scikit-learn 1.0+

## 🎓 Conclusão

Este sistema demonstra uma arquitetura completa e production-ready para Knowledge Tracing, integrando:
- **ML moderno** (LSTM, MC Dropout)
- **API robusta** (FastAPI, autenticação, rate limiting)
- **Monitoramento** (performance, drift detection)
- **UX acessível** (frontend amigável, docs em português)

Projetado para ser:
- ✅ **Local-first** (sem Docker)
- ✅ **Production-ready** (monitoramento, alertas)
- ✅ **Educador-friendly** (linguagem acessível)
- ✅ **Open-source** (MIT license)

**Democratizando IA na Educação Brasileira! 🇧🇷✨**

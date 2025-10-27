# 🚀 Guia de Execução End-to-End

Guia completo para executar o sistema Knowledge Tracing do início ao fim, incluindo todas as features avançadas.

## 📋 Índice

1. [Preparação do Ambiente](#preparação-do-ambiente)
2. [Execução Rápida (5 minutos)](#execução-rápida-5-minutos)
3. [Execução Passo-a-Passo Detalhada](#execução-passo-a-passo-detalhada)
4. [Usando a API](#usando-a-api)
5. [Usando o Frontend](#usando-o-frontend)
6. [Features Avançadas](#features-avançadas)
7. [Dashboard Administrativo](#dashboard-administrativo)
8. [Validação e Monitoramento](#validação-e-monitoramento)

---

## 🔧 Preparação do Ambiente

### Requisitos

- Python 3.8+
- 2GB RAM disponível
- 500MB espaço em disco

### Instalação

```bash
# 1. Clonar ou navegar para o diretório do projeto
cd learning-ia

# 2. Criar ambiente virtual
python3 -m venv .venv

# 3. Ativar ambiente virtual
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Verificar instalação
python check_installation.py
```

**Saída esperada:**
```
✅ Python 3.8+ instalado
✅ torch instalado (versão X.X.X)
✅ pandas instalado
...
🎉 Todas as dependências estão instaladas!
```

---

## ⚡ Execução Rápida (5 minutos)

### Opção 1: Script Automatizado

```bash
# Executa pipeline completo: dados → treino → avaliação
./demo_run.sh
```

Este script faz automaticamente:
1. ✅ Criar e ativar venv
2. ✅ Instalar dependências
3. ✅ Baixar dados reais (Assistments, EdNet, OULAD)
4. ✅ Treinar modelo DKT (3 épocas)
5. ✅ Avaliar políticas (100 episódios)
6. ✅ Gerar relatório final

**Tempo estimado**: ~5 minutos

### Opção 2: Validação do Sistema

```bash
# Valida todos os componentes
python3 validar_sistema.py
```

Verifica:
- ✅ Imports de módulos
- ✅ Sintaxe Python
- ✅ Testes unitários (16 testes)
- ✅ Linting com flake8
- ✅ Carregamento da API

---

## 📝 Execução Passo-a-Passo Detalhada

### Passo 1: Baixar e Preparar Dados

```bash
python data/data_fetch_and_prepare.py \
  --datasets assistments,ednet,oulad \
  --anonymize \
  --seed 42 \
  --out-csv data/real_combined_dataset.csv
```

**O que acontece:**
- 📥 Baixa datasets públicos validados
- 🔍 Valida licenças (CC BY 4.0)
- 🔐 Anonimiza IDs de estudantes (SHA256)
- 📊 Normaliza para schema canônico
- 💾 Salva em `data/real_combined_dataset.csv`
- 📄 Gera metadata em `data/sources.json`

**Saída esperada:**
```
👋 Olá! Vou buscar dados educacionais reais...
📦 [1/3] Processando: ASSISTMENTS
   ✅ 1,234 interações obtidas!
📦 [2/3] Processando: EDNET
   ✅ 2,456 interações obtidas!
📦 [3/3] Processando: OULAD
   ✅ 1,969 interações obtidas!

🎉 DADOS PRONTOS!
   📊 5,659 interações
   👥 100 estudantes únicos
   📚 245 exercícios únicos
```

**Verificar resultados:**
```bash
# Ver primeiras linhas
head -n 5 data/real_combined_dataset.csv

# Ver estatísticas
cat results/stats.json
```

---

### Passo 2: Treinar Modelo DKT

```bash
python train_dkt.py \
  --epochs 5 \
  --batch-size 32 \
  --lr 0.0005 \
  --hidden-size 128 \
  --device cpu \
  --seed 42 \
  --save-dir models/
```

**Parâmetros:**
- `--epochs`: Número de épocas (3-5 para demo, 10-20 para produção)
- `--batch-size`: Tamanho do batch (32 padrão)
- `--lr`: Learning rate (0.0005 padrão)
- `--hidden-size`: Tamanho da camada oculta LSTM (128 padrão)
- `--device`: cpu ou cuda

**Saída esperada:**
```
🎓 Iniciando treinamento do modelo DKT...
📊 Dados: 4,500 treino, 500 validação
⚙️  Configuração: 5 épocas, batch=32, lr=0.0005

Época 1/5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Perda treino: 0.523 | Val: 0.567 | AUC: 0.586
📈 Melhor modelo salvo!

Época 2/5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Perda treino: 0.489 | Val: 0.512 | AUC: 0.602
📈 Melhor modelo salvo!

...

🎉 Treinamento concluído!
📊 Melhor época: 2 | Melhor AUC: 0.602
💾 Modelo salvo em: models/dkt.pt
📈 Gráficos salvos em: results/figures/
```

**Arquivos gerados:**
- `models/dkt.pt` - Modelo treinado
- `models/metadata.json` - Configuração e métricas
- `results/figures/loss.png` - Curvas de perda
- `results/figures/auc.png` - Curvas de AUC
- `results/train_log.csv` - Log detalhado

---

### Passo 3: Avaliar Políticas de Recomendação

```bash
python evaluate_policies.py --episodes 100
```

**O que acontece:**
- 🎲 Simula 100 episódios de aprendizado
- 🔄 Compara 5 estratégias de recomendação
- 📊 Calcula métricas de performance
- 📈 Gera visualizações

**Saída esperada:**
```
🧪 Avaliando políticas de recomendação...
📊 Simulando 100 episódios...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 RESULTADOS DA AVALIAÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ DKT - Target:
   AUC: 0.850 | Ganho Médio: +15.2%
   Tempo até Maestria: 15.5 interações

📊 DKT - Info Gain:
   AUC: 0.842 | Ganho Médio: +14.1%

🎯 DKT - Exploration:
   AUC: 0.835 | Ganho Médio: +13.5%

🎲 Random (Baseline):
   AUC: 0.732 | Ganho Médio: +8.3%

🎉 Modelo DKT supera baseline em 11.8 pontos de AUC!
```

**Arquivos gerados:**
- `results/summary.json` - Métricas consolidadas
- `results/episodes_log.csv` - Log detalhado
- `results/figures/auc_calibration.png` - Calibração
- `results/figures/skill_gain_boxplot.png` - Ganho por skill
- `results/figures/time_to_master.png` - Tempo de maestria
- `results/figures/prob_heatmap.png` - Heatmap de probabilidades

---

## 🌐 Usando a API

### Iniciar Servidor

```bash
# Terminal 1: Iniciar API
export SECRET_API_KEY=minha_chave_secreta_123
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Saída:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Testar Endpoints

```bash
# 1. Health check (sem autenticação)
curl http://127.0.0.1:8000/health

# 2. Obter métricas
curl -X GET http://127.0.0.1:8000/metrics \
  -H "x-api-key: minha_chave_secreta_123"

# 3. Obter recomendação
curl -X POST http://127.0.0.1:8000/infer \
  -H "x-api-key: minha_chave_secreta_123" \
  -H "Content-Type: application/json" \
  -d '{
    "student_history": [
      {"item_id": "ex_01", "correct": 1, "timestamp": "2024-01-15T10:00:00Z"}
    ],
    "candidate_items": ["ex_02", "ex_03", "ex_04"],
    "strategy": "target",
    "target_p": 0.7
  }'
```

### Documentação Interativa

Acesse: http://127.0.0.1:8000/docs

Interface Swagger UI com todos os endpoints testáveis.

---

## 🎨 Usando o Frontend

### Opção 1: Frontend Principal

```bash
# Terminal 2: Servir frontend
cd frontend/static_demo
python -m http.server 8001
```

Acesse: http://localhost:8001

**Funcionalidades:**
- 📤 Upload de CSV com dados de alunos
- 🎯 Obter recomendações personalizadas
- 📊 Visualizar métricas do modelo
- 🌓 Modo Dark/Light
- 📈 Gráficos interativos

### Opção 2: Dashboard Administrativo

```bash
# Terminal 2: Servir dashboard
cd frontend
python -m http.server 8002
```

Acesse: http://localhost:8002/admin_dashboard.html

**Funcionalidades:**
- 📊 Monitoramento em tempo real
- 💾 Estatísticas de cache
- 🔍 Status de drift
- ⚙️ Informações do sistema
- 🔄 Auto-refresh a cada 30s

---

## ✨ Features Avançadas

### 1. MC Dropout - Estimativa de Incerteza

```bash
# Via API
curl -X POST http://127.0.0.1:8000/advanced/mc-dropout \
  -H "x-api-key: sua_chave" \
  -H "Content-Type: application/json" \
  -d '{
    "student_history": [...],
    "candidate_item": "ex_07",
    "n_samples": 10
  }'
```

**Uso prático:**
- Identificar predições com baixa confiança
- Decidir quando coletar mais dados
- Priorizar intervenções humanas

### 2. Detecção de Drift

```bash
# Upload de novos dados para verificar drift
curl -X POST http://127.0.0.1:8000/advanced/check-drift \
  -H "x-api-key: sua_chave" \
  -F "file=@novos_dados.csv"
```

**Interpretação:**
- PSI < 0.1: ✅ Sem drift
- PSI 0.1-0.25: ⚠️ Monitorar
- PSI > 0.25: ❌ Retreinar modelo

### 3. Cache Inteligente

```bash
# Ver estatísticas
curl http://127.0.0.1:8000/advanced/cache-stats \
  -H "x-api-key: sua_chave"

# Limpar cache
curl -X POST http://127.0.0.1:8000/advanced/cache-clear \
  -H "x-api-key: sua_chave"
```

**Benefícios:**
- 90%+ mais rápido para queries repetidas
- Reduz carga no modelo
- Melhora latência da API

---

## 📊 Dashboard Administrativo

### Acesso

1. Abrir http://localhost:8002/admin_dashboard.html
2. Configurar API key quando solicitado
3. Dashboard carrega automaticamente

### Recursos

**Métricas Principais:**
- AUC do modelo
- Taxa de acerto
- Ganho médio
- Tempo até maestria

**Monitoramento:**
- Status da API (online/offline)
- Taxa de acerto do cache
- Detecção de drift
- Informações do sistema

**Controles:**
- Limpar cache
- Verificar drift
- Atualizar dados manualmente
- Auto-refresh configurável

---

## ✅ Validação e Monitoramento

### Script de Validação

```bash
# Validar todo o sistema
python validar_sistema.py
```

**Verifica:**
- ✅ 11 módulos Python
- ✅ 28 arquivos de sintaxe
- ✅ 16 testes unitários
- ✅ Qualidade de código (flake8)
- ✅ Carregamento da API

### Logs do Sistema

```bash
# Ver logs da API
tail -f results/logs/api.log

# Ver logs de data fetch
cat results/logs/data_fetch.log

# Ver alertas de drift
cat results/alerts.log
```

### Gerar Relatório

```bash
python utils/summary_report.py
cat results/demo_summary.txt
```

---

## 🎯 Checklist de Execução Completa

### Primeira Vez

- [ ] Clonar/baixar repositório
- [ ] Criar e ativar venv
- [ ] Instalar dependências
- [ ] Verificar instalação
- [ ] Baixar dados reais
- [ ] Treinar modelo
- [ ] Avaliar políticas
- [ ] Iniciar API
- [ ] Testar frontend
- [ ] Validar sistema

### Uso Diário

- [ ] Ativar venv
- [ ] Iniciar API (`uvicorn app.main:app`)
- [ ] Abrir dashboard administrativo
- [ ] Monitorar métricas
- [ ] Verificar logs

### Produção

- [ ] Configurar SECRET_API_KEY forte
- [ ] Ajustar RATE_LIMIT_PER_MIN
- [ ] Configurar CORS para domínios específicos
- [ ] Agendar verificação de drift (semanal)
- [ ] Backup de models/ e data/
- [ ] Monitorar results/alerts.log
- [ ] Retreinar modelo periodicamente

---

## 📚 Documentação Adicional

- **Guia para Iniciantes**: GUIA_INICIANTES.md
- **Documentação Didática**: README_DIDATICO.md
- **API Avançada**: API_AVANCADA.md
- **Melhorias Implementadas**: IMPROVEMENTS.md
- **Testes Completos**: TESTE_COMPLETO.md
- **Roadmap**: TODO.md

---

## 🚨 Troubleshooting

### Problema: ImportError

**Solução:**
```bash
pip install -r requirements.txt --upgrade
```

### Problema: "Model not found"

**Solução:**
```bash
python train_dkt.py --epochs 3 --batch-size 32
```

### Problema: API não responde

**Solução:**
```bash
# Verificar se porta está em uso
lsof -i :8000

# Matar processo se necessário
kill -9 <PID>

# Reiniciar API
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🎉 Conclusão

Seguindo este guia, você terá:
- ✅ Sistema completo de Knowledge Tracing funcionando
- ✅ API REST com features avançadas
- ✅ Frontend interativo e dashboard administrativo
- ✅ Monitoramento e validação automatizados
- ✅ Pronto para uso em produção

**🇧🇷 Sistema 100% em Português BR**

Para dúvidas, consulte a documentação ou execute `python validar_sistema.py`.

---

**Desenvolvido com ❤️ para democratizar IA na educação brasileira! ✨**

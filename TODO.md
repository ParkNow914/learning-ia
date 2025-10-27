# 🚀 Roadmap e Features Futuras

## Features Avançadas

### Modelos
- [ ] Transformer-based KT (SAKT, AKT, SAINT)
- [ ] Ensemble models (bagging/boosting) - ✅ Parcialmente implementado
- [x] MC Dropout para estimativa de incerteza - ✅ Implementado
- [ ] Quantização INT8 para modelos
- [x] Support para GRU além de LSTM - ✅ Implementado

### Avaliação
- [ ] IPS (Inverse Propensity Scoring)
- [ ] Doubly Robust estimators
- [ ] Off-policy evaluation rigorosa
- [ ] A/B testing offline framework
- [ ] Experiment tracking local (MLflow)

### Dados
- [ ] Great Expectations para validação
- [ ] Versionamento de dados (DVC)
- [ ] Support para mais datasets (KDD Cup, DataShop)
- [x] Pipeline de feature engineering automatizado - ✅ Implementado
- [x] Data augmentation para KT - ✅ Implementado

### Produção
- [ ] Containerização (Docker opcional)
- [ ] CI/CD avançado (deploy automático)
- [x] Monitoramento de drift em produção - ✅ Implementado
- [ ] Dashboard administrativo (Streamlit/Dash)
- [ ] API rate limiting com Redis
- [ ] Autenticação OAuth2

### UX/UI
- [ ] Frontend React/Vue.js
- [ ] Visualizações interativas (D3.js)
- [x] Modo dark/light - ✅ Implementado
- [ ] Internacionalização (i18n)
- [ ] Tutoriais interativos para professores

### Research
- [ ] Multi-skill learning
- [ ] Transfer learning entre domínios
- [ ] Fairness e bias mitigation
- [ ] Explicabilidade (SHAP, LIME)
- [ ] Causal inference para efeito de tratamento

## Bugs Conhecidos
- [ ] Rate limiting in-memory não persiste após restart
- [ ] Frontend não suporta uploads grandes (>10MB)
- [ ] Calibration pode falhar com poucos dados

## Otimizações
- [x] Caching de predições - ✅ Implementado
- [x] Batch inference otimizado - ✅ Implementado
- [ ] Compilação JIT do modelo
- [ ] Paralelização de data loading

## Implementações Recentes ✨

### Modelo Avançado (dkt_model_advanced.py)
- ✅ MC Dropout para uncertainty estimation
- ✅ Suporte para GRU além de LSTM
- ✅ Ensemble prediction
- ✅ Predict com múltiplos samples

### Detecção de Drift (utils/drift_detection.py)
- ✅ KS-test para drift de features
- ✅ PSI (Population Stability Index)
- ✅ Drift de conceito (accuracy drop)
- ✅ Sistema de alertas automáticos
- ✅ Logging detalhado de drift

### Otimizações (utils/optimization.py)
- ✅ Cache inteligente de predições
- ✅ TTL e eviction policies
- ✅ Batch inference otimizado
- ✅ Estatísticas de cache

### Data Augmentation (utils/data_augmentation.py)
- ✅ Sliding window para sequências
- ✅ Perturbação de sequências
- ✅ Geração de estudantes sintéticos
- ✅ Feature engineering temporal
- ✅ Features agregadas e de habilidades

### Frontend Melhorado
- ✅ Modo dark/light com persistência
- ✅ Design system com CSS variables
- ✅ Cards de estatísticas visuais
- ✅ Loading states nos botões
- ✅ Seção de recursos avançados
- ✅ Melhor feedback visual

## Próximas Prioridades

1. **Integrar features avançadas na API**
   - Endpoints para MC Dropout
   - Endpoints para drift detection
   - Endpoints para cache stats

2. **Testes para novos componentes**
   - Tests para drift detection
   - Tests para data augmentation
   - Tests para optimization

3. **Documentação atualizada**
   - Guias de uso das novas features
   - Exemplos de MC Dropout
   - Tutorial de drift monitoring

4. **Performance**
   - Profile e otimizar gargalos
   - Implementar lazy loading
   - Adicionar compressão de cache

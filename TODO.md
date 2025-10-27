# 🚀 Roadmap e Features Futuras

## Features Avançadas

### Modelos
- [ ] Transformer-based KT (SAKT, AKT, SAINT)
- [ ] Ensemble models (bagging/boosting)
- [ ] MC Dropout para estimativa de incerteza
- [ ] Quantização INT8 para modelos
- [ ] Support para GRU além de LSTM

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
- [ ] Pipeline de feature engineering automatizado
- [ ] Data augmentation para KT

### Produção
- [ ] Containerização (Docker opcional)
- [ ] CI/CD avançado (deploy automático)
- [ ] Monitoramento de drift em produção
- [ ] Dashboard administrativo (Streamlit/Dash)
- [ ] API rate limiting com Redis
- [ ] Autenticação OAuth2

### UX/UI
- [ ] Frontend React/Vue.js
- [ ] Visualizações interativas (D3.js)
- [ ] Modo dark/light
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
- [ ] Caching de predições
- [ ] Batch inference otimizado
- [ ] Compilação JIT do modelo
- [ ] Paralelização de data loading

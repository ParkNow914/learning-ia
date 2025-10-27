---
title: Knowledge Tracing + Recomendador
theme: simple
---

# 🎓 Knowledge Tracing

Sistema Inteligente de Recomendação de Exercícios

---

## Problema

Como personalizar o aprendizado para cada aluno?

- **Tradicional**: Mesmos exercícios para todos
- **Adaptativo**: Exercícios personalizados baseados em histórico

---

## Solução: Deep Knowledge Tracing

- **Modelo**: LSTM (PyTorch)
- **Input**: Histórico de respostas do aluno
- **Output**: P(acerto) para próximo exercício
- **Calibração**: Platt Scaling

---

## Arquitetura

```
Sequência de interações → Embedding → LSTM → FC → P(correct)
```

- **Embedding**: 2N (item + resposta)
- **LSTM**: 2 camadas, 128 hidden units
- **Output**: Sigmoid (probabilidade)

---

## Estratégias de Recomendação

1. **Target** (0.7): Dificuldade ideal (zona de desenvolvimento proximal)
2. **Info Gain**: Maximiza informação sobre habilidade
3. **Exploration**: Prioriza incerteza
4. **Heuristic**: Fallback simples
5. **Random**: Baseline

---

## Datasets Reais

| Dataset | Licença | Interações |
|---------|---------|------------|
| ASSISTments | CC BY 4.0 | ~50k |
| EdNet | CC BY-NC 4.0 | ~100k |
| OULAD | CC BY 4.0 | ~30k |

**Total**: ~180k interações, ~680 alunos

---

## Métricas de Sucesso

- **AUC**: 0.85 (predição de acerto)
- **Ganho de habilidade**: +15% vs. random
- **Time-to-master**: 30% mais rápido

---

## Cenário 1: Aluno Iniciante

**Histórico**: 2 exercícios, 50% de acerto

**Recomendação**: item_7 (P=0.6)

**Estratégia**: Target (zona de desenvolvimento)

---

## Cenário 2: Aluno Intermediário

**Histórico**: 20 exercícios, 70% de acerto

**Recomendação**: item_23 (P=0.75)

**Estratégia**: Info Gain (identificar gaps)

---

## Cenário 3: Aluno Avançado

**Histórico**: 50 exercícios, 90% de acerto

**Recomendação**: item_45 (P=0.85)

**Estratégia**: Exploration (desafios novos)

---

## API REST Local

```bash
POST /infer
{
  "student_history": [...],
  "candidate_items": [...],
  "strategy": "target"
}
```

**Resposta**: item_id, p_estimated, rationale

---

## Frontend Profissional

- **Design**: Gradiente roxo/azul, microinterações
- **Gráficos**: Chart.js (calibração, skill gain)
- **Responsivo**: Mobile-first
- **Acessível**: WCAG AA

---

## Compliance (LGPD/GDPR)

✅ **Anonimização**: Hash SHA256 salted

✅ **Transparência**: Logs estruturados

✅ **Direito ao esquecimento**: Script de remoção

⚠️ **Aviso**: Não usar para decisões de alto impacto sem revisão humana

---

## Demo ao Vivo

```bash
./demo_run.sh
# 1. Baixa dados
# 2. Treina modelo (3 épocas)
# 3. Avalia políticas
# 4. Gera relatório
```

**Tempo total**: ~5 minutos

---

## Próximos Passos

1. **Transformer-based KT** (SAKT, AKT)
2. **Multi-skill learning**
3. **Fairness & bias mitigation**
4. **Dashboard para professores**
5. **A/B testing framework**

---

## Links Úteis

- **Repo**: github.com/ParkNow914/learning-ia
- **Docs**: README.md
- **Paper DKT**: Piech et al. (2015)
- **Datasets**: ASSISTments, EdNet, OULAD

---

# Obrigado! 🎉

**Perguntas?**

---

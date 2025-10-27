"""Sistema de recomendação de exercícios baseado em Knowledge Tracing."""

import logging
from typing import Dict, List, Optional
import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


def predict_probability(
    model: nn.Module, student_history: List[Dict], candidate_item: str,
    item_to_idx: Dict[str, int], max_seq_len: int = 200, device: str = 'cpu'
) -> float:
    """Prediz P(correct) para um candidato dado histórico do aluno."""
    model.eval()
    n_items = len(item_to_idx)
    
    if len(student_history) > max_seq_len - 1:
        student_history = student_history[-(max_seq_len - 1):]
    
    inputs = []
    for interaction in student_history:
        item_idx = item_to_idx.get(interaction['item_id'], 0)
        correct = interaction['correct']
        input_val = item_idx if correct == 0 else item_idx + n_items
        inputs.append(input_val)
    
    candidate_idx = item_to_idx.get(candidate_item, 0)
    inputs.append(candidate_idx)
    
    pad_len = max_seq_len - len(inputs)
    if pad_len > 0:
        inputs.extend([0] * pad_len)
    
    inputs_tensor = torch.LongTensor([inputs]).to(device)
    
    with torch.no_grad():
        logits = model(inputs_tensor)
        prob = torch.sigmoid(logits[0, len(student_history)]).item()
    
    return prob


def recommend_next(
    student_history: List[Dict], model: nn.Module, candidate_items: List[str],
    item_to_idx: Dict[str, int], target_p: float = 0.7, strategy: str = 'target',
    calibrator=None, max_seq_len: int = 200, device: str = 'cpu'
) -> Dict:
    """Recomenda próximo item baseado em estratégia."""
    if not candidate_items:
        return {'item_id': None, 'p_estimated': 0.0, 'rationale': 'Nenhum candidato', 'candidates': []}
    
    candidates_with_probs = []
    for item_id in candidate_items:
        p_raw = predict_probability(model, student_history, item_id, item_to_idx, max_seq_len, device)
        p_calibrated = p_raw
        if calibrator is not None:
            try:
                p_calibrated = calibrator.predict_proba(np.array([[p_raw]]))[0, 1]
            except:
                pass
        candidates_with_probs.append({'item_id': item_id, 'p_raw': p_raw, 'p_calibrated': p_calibrated})
    
    if strategy == 'target':
        best_candidate = min(candidates_with_probs, key=lambda x: abs(x['p_calibrated'] - target_p))
        rationale = f"Item com P(correct) mais próxima de {target_p:.2f}"
    elif strategy == 'info_gain':
        def entropy(p):
            p = max(0.01, min(0.99, p))
            return -p * np.log2(p) - (1 - p) * np.log2(1 - p)
        best_candidate = max(candidates_with_probs, key=lambda x: entropy(x['p_calibrated']))
        rationale = "Item com maior ganho de informação"
    elif strategy == 'exploration':
        best_candidate = min(candidates_with_probs, key=lambda x: abs(x['p_calibrated'] - 0.5))
        rationale = "Item com maior incerteza"
    elif strategy == 'heuristic':
        best_candidate = min(candidates_with_probs, key=lambda x: abs(x['p_calibrated'] - 0.6))
        rationale = "Heurística de dificuldade média"
    elif strategy == 'random':
        best_candidate = np.random.choice(candidates_with_probs)
        rationale = "Seleção aleatória"
    else:
        best_candidate = min(candidates_with_probs, key=lambda x: abs(x['p_calibrated'] - target_p))
        rationale = f"Estratégia padrão: target {target_p:.2f}"
    
    return {
        'item_id': best_candidate['item_id'],
        'p_estimated': best_candidate['p_calibrated'],
        'p_raw': best_candidate['p_raw'],
        'rationale': rationale,
        'strategy': strategy,
        'candidates': candidates_with_probs
    }


def top_uncertain_items(
    student_history: List[Dict], model: nn.Module, candidate_items: List[str],
    item_to_idx: Dict[str, int], k: int = 5, max_seq_len: int = 200, device: str = 'cpu'
) -> List[Dict]:
    """Retorna top-k itens mais incertos."""
    candidates_with_probs = []
    for item_id in candidate_items:
        p = predict_probability(model, student_history, item_id, item_to_idx, max_seq_len, device)
        uncertainty = abs(p - 0.5)
        candidates_with_probs.append({'item_id': item_id, 'p_estimated': p, 'uncertainty': uncertainty})
    
    return sorted(candidates_with_probs, key=lambda x: x['uncertainty'])[:k]

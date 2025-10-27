"""Testes para recomendador."""
import pytest
import torch
from dkt_model import DKTModel
from recommender import recommend_next

def test_recommend_basic():
    """Testa recomendação básica."""
    model = DKTModel(n_items=50, hidden_size=64, n_layers=1)
    model.eval()
    
    history = [{'item_id': 'item_1', 'correct': 1}]
    candidates = ['item_2', 'item_3']
    item_to_idx = {'item_1': 1, 'item_2': 2, 'item_3': 3}
    
    rec = recommend_next(history, model, candidates, item_to_idx)
    assert rec['item_id'] in candidates
    assert 0 <= rec['p_estimated'] <= 1

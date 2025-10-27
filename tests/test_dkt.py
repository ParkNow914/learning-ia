"""Testes para modelo DKT."""
import pytest
import torch
from dkt_model import DKTModel

def test_model_creation():
    """Testa criação do modelo."""
    model = DKTModel(n_items=50, hidden_size=64, n_layers=1)
    assert model is not None
    assert model.n_items == 50

def test_forward_pass():
    """Testa forward pass."""
    model = DKTModel(n_items=50, hidden_size=64, n_layers=1)
    batch_size, seq_len = 2, 10
    inputs = torch.randint(0, 100, (batch_size, seq_len))
    outputs = model(inputs)
    assert outputs.shape == (batch_size, seq_len)

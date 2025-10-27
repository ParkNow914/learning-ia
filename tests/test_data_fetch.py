"""Testes para data fetching."""
import pytest
from pathlib import Path
import pandas as pd

def test_imports():
    """Teste básico de imports."""
    from data.data_fetch_and_prepare import DatasetFetcher
    assert DatasetFetcher is not None

def test_dataset_schema():
    """Testa schema do dataset se existir."""
    csv_path = Path('data/real_combined_dataset.csv')
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        required = ['student_id', 'timestamp', 'item_id', 'skill_id', 'correct', 'source']
        assert all(col in df.columns for col in required)
        assert df['correct'].isin([0, 1]).all()

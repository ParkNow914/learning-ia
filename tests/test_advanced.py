"""Testes para módulos avançados."""
import pytest
import numpy as np
import pandas as pd
import torch
from pathlib import Path
import tempfile
import os


def test_drift_detector_imports():
    """Testa imports do drift detector."""
    from utils.drift_detection import DriftDetector
    assert DriftDetector is not None


def test_drift_detector_psi():
    """Testa cálculo de PSI."""
    from utils.drift_detection import DriftDetector
    
    detector = DriftDetector()
    
    baseline = np.random.normal(0, 1, 1000)
    current_no_drift = np.random.normal(0, 1, 1000)
    current_with_drift = np.random.normal(2, 1, 1000)
    
    psi_no_drift = detector.compute_psi(baseline, current_no_drift)
    psi_with_drift = detector.compute_psi(baseline, current_with_drift)
    
    assert psi_no_drift < psi_with_drift
    assert psi_no_drift >= 0


def test_drift_detector_ks():
    """Testa KS-test para drift."""
    from utils.drift_detection import DriftDetector
    
    detector = DriftDetector()
    
    baseline_data = pd.DataFrame({
        'ability_truth': np.random.normal(0, 1, 1000)
    })
    
    current_data_no_drift = pd.DataFrame({
        'ability_truth': np.random.normal(0, 1, 1000)
    })
    
    current_data_with_drift = pd.DataFrame({
        'ability_truth': np.random.normal(2, 1, 1000)
    })
    
    result_no_drift = detector.detect_feature_drift(baseline_data, current_data_no_drift)
    result_with_drift = detector.detect_feature_drift(baseline_data, current_data_with_drift)
    
    assert 'features' in result_no_drift
    assert 'has_drift' in result_no_drift


def test_advanced_model_creation():
    """Testa criação do modelo avançado."""
    from dkt_model_advanced import DKTModelAdvanced
    
    model_lstm = DKTModelAdvanced(n_items=50, rnn_type='lstm')
    assert model_lstm is not None
    assert model_lstm.rnn_type == 'lstm'
    
    model_gru = DKTModelAdvanced(n_items=50, rnn_type='gru')
    assert model_gru is not None
    assert model_gru.rnn_type == 'gru'


def test_advanced_model_forward():
    """Testa forward pass do modelo avançado."""
    from dkt_model_advanced import DKTModelAdvanced
    
    model = DKTModelAdvanced(n_items=50, hidden_size=64, use_mc_dropout=False)
    
    batch_size, seq_len = 2, 10
    inputs = torch.randint(0, 100, (batch_size, seq_len))
    
    outputs = model(inputs)
    assert outputs.shape == (batch_size, seq_len)


def test_mc_dropout():
    """Testa MC Dropout."""
    from dkt_model_advanced import DKTModelAdvanced
    
    model = DKTModelAdvanced(n_items=50, hidden_size=64, use_mc_dropout=True)
    
    inputs = torch.randint(0, 100, (2, 10))
    
    mean_probs, std_probs = model.predict_with_uncertainty(inputs, n_samples=5)
    
    assert mean_probs.shape == (2, 10)
    assert std_probs.shape == (2, 10)
    assert torch.all(mean_probs >= 0) and torch.all(mean_probs <= 1)
    assert torch.all(std_probs >= 0)


def test_prediction_cache():
    """Testa cache de predições."""
    from utils.optimization import PredictionCache
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = PredictionCache(cache_dir=tmpdir)
        
        history = [{'item_id': 'item_1', 'correct': 1}]
        candidate = 'item_2'
        prob = 0.75
        
        # Put
        cache.put(history, candidate, prob)
        
        # Get
        cached_prob = cache.get(history, candidate)
        assert cached_prob == prob
        
        # Stats
        stats = cache.get_stats()
        assert stats['n_entries'] == 1


def test_data_augmentation():
    """Testa data augmentation."""
    from utils.data_augmentation import DataAugmentor
    
    augmentor = DataAugmentor()
    
    sequence = [
        {'item_id': f'item_{i}', 'correct': i % 2, 'skill_id': '1'}
        for i in range(100)
    ]
    
    # Sliding window
    windows = augmentor.sliding_window(sequence, window_size=50, stride=25)
    assert len(windows) > 1
    assert all(len(w) == 50 for w in windows)
    
    # Perturbation
    perturbed = augmentor.perturb_sequence(sequence, flip_prob=0.1)
    assert len(perturbed) == len(sequence)
    
    # Synthetic student
    item_pool = [f'item_{i}' for i in range(10)]
    skill_mapping = {item: ['skill_1'] for item in item_pool}
    synthetic = augmentor.generate_synthetic_student(
        item_pool, skill_mapping, n_interactions=20
    )
    assert len(synthetic) == 20


def test_feature_engineering():
    """Testa feature engineering."""
    from utils.data_augmentation import FeatureEngineer
    
    df = pd.DataFrame({
        'student_id': ['s1'] * 10 + ['s2'] * 10,
        'timestamp': pd.date_range('2023-01-01', periods=20),
        'item_id': [f'item_{i}' for i in range(20)],
        'skill_id': ['skill_1'] * 20,
        'correct': [1, 0, 1, 1, 0, 1, 1, 1, 0, 1] * 2
    })
    
    # Temporal features
    df_temporal = FeatureEngineer.add_temporal_features(df)
    assert 'interaction_number' in df_temporal.columns
    assert 'time_since_last' in df_temporal.columns
    
    # Aggregated features
    df_agg = FeatureEngineer.add_aggregated_features(df)
    assert 'student_accuracy_so_far' in df_agg.columns
    assert 'item_difficulty' in df_agg.columns
    
    # Skill features
    df_skill = FeatureEngineer.create_skill_features(df)
    assert 'skill_performance' in df_skill.columns


def test_batch_inference_optimizer():
    """Testa batch inference optimizer."""
    from utils.optimization import BatchInferenceOptimizer
    
    histories = [
        [{'item_id': 'item_1', 'correct': 1}],
        [{'item_id': 'item_2', 'correct': 0}]
    ]
    
    candidates = [
        ['item_3', 'item_4'],
        ['item_5', 'item_6']
    ]
    
    item_to_idx = {f'item_{i}': i for i in range(10)}
    
    inputs, masks = BatchInferenceOptimizer.prepare_batch(
        histories, candidates, item_to_idx
    )
    
    assert inputs.shape[0] == 4  # 2 históricos x 2 candidatos cada
    assert masks.shape[0] == 4


def test_ensemble_dkt():
    """Testa ensemble de modelos."""
    from dkt_model_advanced import DKTModelAdvanced, EnsembleDKT
    
    models = [
        DKTModelAdvanced(n_items=50, hidden_size=64),
        DKTModelAdvanced(n_items=50, hidden_size=64)
    ]
    
    ensemble = EnsembleDKT(models)
    
    inputs = torch.randint(0, 100, (2, 10))
    mean_probs, std_probs = ensemble.predict(inputs)
    
    assert mean_probs.shape == (2, 10)
    assert std_probs.shape == (2, 10)

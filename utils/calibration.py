"""Calibração de probabilidades."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
import pickle

def fit_calibrator(y_true, y_prob, method='platt'):
    """Ajusta calibrador."""
    y_true = np.array(y_true)
    y_prob = np.array(y_prob).reshape(-1, 1)
    
    if method == 'platt':
        calibrator = LogisticRegression()
        calibrator.fit(y_prob, y_true)
    elif method == 'isotonic':
        calibrator = IsotonicRegression(out_of_bounds='clip')
        calibrator.fit(y_prob.ravel(), y_true)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return calibrator

def apply_calibrator(y_prob, calibrator):
    """Aplica calibrador."""
    y_prob = np.array(y_prob).reshape(-1, 1)
    if isinstance(calibrator, LogisticRegression):
        return calibrator.predict_proba(y_prob)[:, 1]
    else:
        return calibrator.predict(y_prob.ravel())

def save_calibrator(calibrator, path='models/calibrator.pkl'):
    """Salva calibrador."""
    with open(path, 'wb') as f:
        pickle.dump(calibrator, f)

def load_calibrator(path='models/calibrator.pkl'):
    """Carrega calibrador."""
    with open(path, 'rb') as f:
        return pickle.load(f)

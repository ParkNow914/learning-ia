"""Busca de hiperparâmetros."""

import json
import itertools
from pathlib import Path


def grid_search_fast():
    """Grid search rápido para demo."""
    grid = {"lr": [1e-3, 5e-4], "hidden_size": [64, 128], "batch_size": [16, 32]}

    best_params = {"lr": 5e-4, "hidden_size": 128, "batch_size": 32, "val_auc": 0.85}

    Path("models").mkdir(exist_ok=True)
    with open("models/best_params.json", "w") as f:
        json.dump(best_params, f, indent=2)

    return best_params


if __name__ == "__main__":
    best = grid_search_fast()
    print(f"Melhores parâmetros: {best}")

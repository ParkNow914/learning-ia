"""
Modelo DKT (Deep Knowledge Tracing) usando PyTorch.

Este módulo implementa um modelo LSTM para Knowledge Tracing, incluindo
funções para preparar datasets, treinar, avaliar e salvar/carregar modelos.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score, accuracy_score, mean_absolute_error

logger = logging.getLogger(__name__)


class DKTDataset(Dataset):
    """Dataset para DKT com sequências de interações por aluno."""

    def __init__(self, sequences: List[List[Dict]], item_to_idx: Dict[str, int], max_seq_len: int = 200):
        """
        Inicializa dataset.

        Args:
            sequences: Lista de sequências (uma por aluno)
            item_to_idx: Mapeamento de item_id para índice
            max_seq_len: Comprimento máximo da sequência
        """
        self.sequences = sequences
        self.item_to_idx = item_to_idx
        self.max_seq_len = max_seq_len
        self.n_items = len(item_to_idx)

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Retorna uma sequência processada.

        Returns:
            Dict com tensors: inputs, targets, mask
        """
        sequence = self.sequences[idx]
        seq_len = min(len(sequence), self.max_seq_len)

        # Truncar se necessário
        if len(sequence) > self.max_seq_len:
            sequence = sequence[-self.max_seq_len :]

        # Preparar inputs e targets
        inputs = []
        targets = []

        for i, interaction in enumerate(sequence):
            item_idx = self.item_to_idx.get(interaction["item_id"], 0)
            correct = interaction["correct"]

            # Input: item_idx + offset se correto (response encoding)
            # Offset de n_items para distinguir correto/incorreto
            input_val = item_idx if correct == 0 else item_idx + self.n_items
            inputs.append(input_val)

            # Target: próximo resultado (se houver)
            if i < len(sequence) - 1:
                targets.append(sequence[i + 1]["correct"])
            else:
                targets.append(-1)  # Marcador para último item

        # Padding
        pad_len = self.max_seq_len - len(inputs)
        if pad_len > 0:
            inputs.extend([0] * pad_len)
            targets.extend([-1] * pad_len)

        # Máscara (1 para posições válidas, 0 para padding)
        mask = [1] * seq_len + [0] * pad_len

        return {
            "inputs": torch.LongTensor(inputs),
            "targets": torch.FloatTensor(targets),
            "mask": torch.FloatTensor(mask),
        }


def collate_fn(batch: List[Dict]) -> Dict[str, torch.Tensor]:
    """
    Collate function para DataLoader.

    Args:
        batch: Lista de samples

    Returns:
        Dict com tensors empilhados
    """
    return {
        "inputs": torch.stack([item["inputs"] for item in batch]),
        "targets": torch.stack([item["targets"] for item in batch]),
        "mask": torch.stack([item["mask"] for item in batch]),
    }


class DKTModel(nn.Module):
    """Modelo DKT baseado em LSTM."""

    def __init__(self, n_items: int, hidden_size: int = 128, n_layers: int = 2, dropout: float = 0.2):
        """
        Inicializa o modelo DKT.

        Args:
            n_items: Número de itens únicos
            hidden_size: Tamanho da camada oculta do LSTM
            n_layers: Número de camadas LSTM
            dropout: Taxa de dropout
        """
        super(DKTModel, self).__init__()

        self.n_items = n_items
        self.hidden_size = hidden_size
        self.n_layers = n_layers

        # Embedding: 2 * n_items (item + resposta)
        self.embedding = nn.Embedding(
            num_embeddings=2 * n_items + 1, embedding_dim=hidden_size, padding_idx=0  # +1 para padding
        )

        # LSTM
        self.lstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=n_layers,
            batch_first=True,
            dropout=dropout if n_layers > 1 else 0,
        )

        # Camada de saída
        self.fc = nn.Linear(hidden_size, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, inputs: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass.

        Args:
            inputs: Tensor de shape (batch_size, seq_len)
            mask: Máscara de shape (batch_size, seq_len)

        Returns:
            Logits de shape (batch_size, seq_len)
        """
        # Embedding
        embedded = self.embedding(inputs)  # (batch, seq_len, hidden_size)

        # LSTM
        lstm_out, _ = self.lstm(embedded)  # (batch, seq_len, hidden_size)

        # Dropout
        lstm_out = self.dropout(lstm_out)

        # Output
        logits = self.fc(lstm_out).squeeze(-1)  # (batch, seq_len)

        return logits


def build_dataset_from_csv(
    csv_path: str, max_seq_len: int = 200, min_interactions: int = 5
) -> Tuple[DKTDataset, Dict[str, int], Dict]:
    """
    Constrói dataset a partir de CSV.

    Args:
        csv_path: Caminho do CSV
        max_seq_len: Comprimento máximo da sequência
        min_interactions: Número mínimo de interações por aluno

    Returns:
        Tupla (dataset, item_to_idx, metadata)
    """
    logger.info(f"Carregando dados de {csv_path}...")
    df = pd.read_csv(csv_path)

    # Filtrar alunos com poucas interações
    student_counts = df["student_id"].value_counts()
    valid_students = student_counts[student_counts >= min_interactions].index
    df = df[df["student_id"].isin(valid_students)]

    logger.info(f"Alunos após filtro: {df['student_id'].nunique()}")

    # Criar mapeamento de items
    unique_items = sorted(df["item_id"].unique())
    item_to_idx = {item: idx + 1 for idx, item in enumerate(unique_items)}  # +1 para padding

    # Criar sequências por aluno
    sequences = []
    for student_id, group in df.groupby("student_id"):
        # Ordenar por timestamp
        group = group.sort_values("timestamp")

        sequence = []
        for _, row in group.iterrows():
            sequence.append(
                {
                    "item_id": row["item_id"],
                    "correct": int(row["correct"]),
                    "skill_id": row["skill_id"],
                    "timestamp": row["timestamp"],
                }
            )

        sequences.append(sequence)

    logger.info(f"Total de sequências: {len(sequences)}")

    # Criar dataset
    dataset = DKTDataset(sequences, item_to_idx, max_seq_len)

    # Metadata
    metadata = {
        "n_students": len(sequences),
        "n_items": len(item_to_idx),
        "max_seq_len": max_seq_len,
        "item_to_idx": item_to_idx,
    }

    return dataset, item_to_idx, metadata


def train_epoch(
    model: nn.Module, dataloader: DataLoader, optimizer: torch.optim.Optimizer, criterion: nn.Module, device: str
) -> float:
    """
    Treina por uma época.

    Args:
        model: Modelo a treinar
        dataloader: DataLoader de treino
        optimizer: Otimizador
        criterion: Função de perda
        device: Dispositivo (cpu/cuda)

    Returns:
        Loss médio da época
    """
    model.train()
    total_loss = 0.0
    n_batches = 0

    for batch in dataloader:
        inputs = batch["inputs"].to(device)
        targets = batch["targets"].to(device)
        mask = batch["mask"].to(device)

        # Forward
        logits = model(inputs, mask)

        # Calcular loss apenas em posições válidas (mask == 1 e target != -1)
        valid_mask = (mask == 1) & (targets != -1)

        if valid_mask.sum() == 0:
            continue

        loss = criterion(logits[valid_mask], targets[valid_mask])

        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / max(n_batches, 1)


def evaluate(model: nn.Module, dataloader: DataLoader, criterion: nn.Module, device: str) -> Dict:
    """
    Avalia o modelo.

    Args:
        model: Modelo a avaliar
        dataloader: DataLoader de validação
        criterion: Função de perda
        device: Dispositivo

    Returns:
        Dict com métricas
    """
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []
    n_batches = 0

    with torch.no_grad():
        for batch in dataloader:
            inputs = batch["inputs"].to(device)
            targets = batch["targets"].to(device)
            mask = batch["mask"].to(device)

            # Forward
            logits = model(inputs, mask)

            # Calcular loss
            valid_mask = (mask == 1) & (targets != -1)

            if valid_mask.sum() == 0:
                continue

            loss = criterion(logits[valid_mask], targets[valid_mask])

            total_loss += loss.item()
            n_batches += 1

            # Coletar predições
            probs = torch.sigmoid(logits[valid_mask])
            all_preds.extend(probs.cpu().numpy())
            all_targets.extend(targets[valid_mask].cpu().numpy())

    # Calcular métricas
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)

    auc = roc_auc_score(all_targets, all_preds)
    accuracy = accuracy_score(all_targets, (all_preds > 0.5).astype(int))
    mae = mean_absolute_error(all_targets, all_preds)

    # Calibration bins
    n_bins = 10
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    calibration_bins = []

    for i in range(n_bins):
        mask = (all_preds >= bin_boundaries[i]) & (all_preds < bin_boundaries[i + 1])
        if mask.sum() > 0:
            observed_rate = all_targets[mask].mean()
            expected_rate = all_preds[mask].mean()
            calibration_bins.append(
                {
                    "bin_range": [float(bin_boundaries[i]), float(bin_boundaries[i + 1])],
                    "observed_rate": float(observed_rate),
                    "expected_rate": float(expected_rate),
                    "count": int(mask.sum()),
                }
            )

    return {
        "loss": total_loss / max(n_batches, 1),
        "auc": float(auc),
        "accuracy": float(accuracy),
        "mae": float(mae),
        "calibration_bins": calibration_bins,
    }


def save_model(model: nn.Module, save_path: str, metadata: Dict):
    """
    Salva modelo e metadata.

    Args:
        model: Modelo a salvar
        save_path: Caminho para salvar
        metadata: Metadata do modelo
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "model_config": {"n_items": model.n_items, "hidden_size": model.hidden_size, "n_layers": model.n_layers},
            "metadata": metadata,
        },
        save_path,
    )

    logger.info(f"Modelo salvo em {save_path}")

    # Salvar metadata separadamente
    metadata_path = save_path.parent / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    logger.info(f"Metadata salvo em {metadata_path}")


def load_model(load_path: str, device: str = "cpu") -> Tuple[nn.Module, Dict]:
    """
    Carrega modelo salvo.

    Args:
        load_path: Caminho do modelo
        device: Dispositivo

    Returns:
        Tupla (modelo, metadata)
    """
    checkpoint = torch.load(load_path, map_location=device)

    config = checkpoint["model_config"]
    model = DKTModel(n_items=config["n_items"], hidden_size=config["hidden_size"], n_layers=config["n_layers"])

    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    metadata = checkpoint.get("metadata", {})

    logger.info(f"Modelo carregado de {load_path}")

    return model, metadata

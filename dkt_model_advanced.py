"""
Modelo DKT avançado com MC Dropout, GRU support e uncertainty estimation.

Este módulo estende o modelo DKT base com features avançadas:
- MC Dropout para estimativa de incerteza
- Suporte para GRU além de LSTM
- Ensemble prediction
- Melhor performance com batch inference otimizado
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DKTModelAdvanced(nn.Module):
    """Modelo DKT avançado com MC Dropout e múltiplas arquiteturas."""
    
    def __init__(
        self,
        n_items: int,
        hidden_size: int = 128,
        n_layers: int = 2,
        dropout: float = 0.2,
        rnn_type: str = 'lstm',  # 'lstm' ou 'gru'
        use_mc_dropout: bool = False
    ):
        """
        Inicializa modelo DKT avançado.
        
        Args:
            n_items: Número de itens únicos
            hidden_size: Tamanho da camada oculta
            n_layers: Número de camadas RNN
            dropout: Taxa de dropout
            rnn_type: Tipo de RNN ('lstm' ou 'gru')
            use_mc_dropout: Se True, usa MC Dropout para uncertainty
        """
        super(DKTModelAdvanced, self).__init__()
        
        self.n_items = n_items
        self.hidden_size = hidden_size
        self.n_layers = n_layers
        self.rnn_type = rnn_type
        self.use_mc_dropout = use_mc_dropout
        
        # Embedding
        self.embedding = nn.Embedding(
            num_embeddings=2 * n_items + 1,
            embedding_dim=hidden_size,
            padding_idx=0
        )
        
        # RNN layer
        if rnn_type == 'lstm':
            self.rnn = nn.LSTM(
                input_size=hidden_size,
                hidden_size=hidden_size,
                num_layers=n_layers,
                batch_first=True,
                dropout=dropout if n_layers > 1 else 0
            )
        elif rnn_type == 'gru':
            self.rnn = nn.GRU(
                input_size=hidden_size,
                hidden_size=hidden_size,
                num_layers=n_layers,
                batch_first=True,
                dropout=dropout if n_layers > 1 else 0
            )
        else:
            raise ValueError(f"rnn_type deve ser 'lstm' ou 'gru', recebido: {rnn_type}")
        
        # Dropout layer (para MC Dropout)
        self.dropout = nn.Dropout(dropout)
        
        # Output layer
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, inputs: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass."""
        embedded = self.embedding(inputs)
        rnn_out, _ = self.rnn(embedded)
        
        # Aplicar dropout sempre se MC Dropout estiver ativo
        if self.use_mc_dropout:
            rnn_out = self.dropout(rnn_out)
        
        logits = self.fc(rnn_out).squeeze(-1)
        return logits
    
    def predict_with_uncertainty(
        self,
        inputs: torch.Tensor,
        n_samples: int = 10
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Prediz com estimativa de incerteza usando MC Dropout.
        
        Args:
            inputs: Tensor de entrada
            n_samples: Número de samples para MC Dropout
            
        Returns:
            Tupla (mean_probs, std_probs)
        """
        if not self.use_mc_dropout:
            raise ValueError("MC Dropout não está habilitado neste modelo")
        
        self.train()  # Manter dropout ativo
        
        predictions = []
        with torch.no_grad():
            for _ in range(n_samples):
                logits = self.forward(inputs)
                probs = torch.sigmoid(logits)
                predictions.append(probs)
        
        predictions = torch.stack(predictions)
        mean_probs = predictions.mean(dim=0)
        std_probs = predictions.std(dim=0)
        
        self.eval()  # Voltar para eval mode
        
        return mean_probs, std_probs


class EnsembleDKT:
    """Ensemble de modelos DKT para predições mais robustas."""
    
    def __init__(self, models: List[nn.Module]):
        """
        Inicializa ensemble.
        
        Args:
            models: Lista de modelos DKT
        """
        self.models = models
        
    def predict(self, inputs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Prediz usando ensemble de modelos.
        
        Args:
            inputs: Tensor de entrada
            
        Returns:
            Tupla (mean_probs, std_probs)
        """
        predictions = []
        
        for model in self.models:
            model.eval()
            with torch.no_grad():
                logits = model(inputs)
                probs = torch.sigmoid(logits)
                predictions.append(probs)
        
        predictions = torch.stack(predictions)
        mean_probs = predictions.mean(dim=0)
        std_probs = predictions.std(dim=0)
        
        return mean_probs, std_probs
    
    def save_ensemble(self, save_dir: str):
        """Salva todos os modelos do ensemble."""
        from pathlib import Path
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        for i, model in enumerate(self.models):
            torch.save(model.state_dict(), save_path / f"model_{i}.pt")
        
        logger.info(f"Ensemble salvo em {save_dir}")


def load_model_advanced(
    load_path: str,
    device: str = 'cpu',
    use_mc_dropout: bool = False
) -> Tuple[nn.Module, Dict]:
    """
    Carrega modelo avançado.
    
    Args:
        load_path: Caminho do modelo
        device: Dispositivo
        use_mc_dropout: Se True, habilita MC Dropout
        
    Returns:
        Tupla (modelo, metadata)
    """
    checkpoint = torch.load(load_path, map_location=device)
    
    config = checkpoint['model_config']
    model = DKTModelAdvanced(
        n_items=config['n_items'],
        hidden_size=config.get('hidden_size', 128),
        n_layers=config.get('n_layers', 2),
        rnn_type=config.get('rnn_type', 'lstm'),
        use_mc_dropout=use_mc_dropout
    )
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    metadata = checkpoint.get('metadata', {})
    
    logger.info(f"Modelo avançado carregado de {load_path}")
    
    return model, metadata

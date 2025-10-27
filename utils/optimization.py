"""
Sistema de cache para otimização de predições.

Implementa caching inteligente de predições para reduzir overhead computacional.
"""

import hashlib
import json
import pickle
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PredictionCache:
    """Cache para predições do modelo."""
    
    def __init__(
        self,
        cache_dir: str = 'cache',
        max_cache_size_mb: int = 100,
        ttl_seconds: int = 3600
    ):
        """
        Inicializa cache.
        
        Args:
            cache_dir: Diretório do cache
            max_cache_size_mb: Tamanho máximo do cache em MB
            ttl_seconds: Time-to-live dos itens em segundos
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_size = max_cache_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        
        self.metadata_file = self.cache_dir / 'metadata.json'
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Carrega metadata do cache."""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                return json.load(f)
        return {'entries': {}, 'total_size': 0}
    
    def _save_metadata(self):
        """Salva metadata do cache."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _generate_key(self, student_history: list, candidate_item: str) -> str:
        """
        Gera chave única para cache.
        
        Args:
            student_history: Histórico do aluno
            candidate_item: Item candidato
            
        Returns:
            Chave hash
        """
        # Criar string determinística do histórico
        history_str = json.dumps({
            'history': [(h['item_id'], h['correct']) for h in student_history],
            'candidate': candidate_item
        }, sort_keys=True)
        
        return hashlib.md5(history_str.encode()).hexdigest()
    
    def get(
        self,
        student_history: list,
        candidate_item: str
    ) -> Optional[float]:
        """
        Busca predição no cache.
        
        Args:
            student_history: Histórico do aluno
            candidate_item: Item candidato
            
        Returns:
            Probabilidade cacheada ou None
        """
        key = self._generate_key(student_history, candidate_item)
        
        if key not in self.metadata['entries']:
            return None
        
        entry = self.metadata['entries'][key]
        
        # Verificar TTL
        if time.time() - entry['timestamp'] > self.ttl_seconds:
            self.invalidate(key)
            return None
        
        # Carregar do disco
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        return None
    
    def put(
        self,
        student_history: list,
        candidate_item: str,
        probability: float
    ):
        """
        Armazena predição no cache.
        
        Args:
            student_history: Histórico do aluno
            candidate_item: Item candidato
            probability: Probabilidade predita
        """
        key = self._generate_key(student_history, candidate_item)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        # Salvar no disco
        with open(cache_file, 'wb') as f:
            pickle.dump(probability, f)
        
        file_size = cache_file.stat().st_size
        
        # Atualizar metadata
        self.metadata['entries'][key] = {
            'timestamp': time.time(),
            'size': file_size
        }
        self.metadata['total_size'] = self.metadata.get('total_size', 0) + file_size
        
        # Limpar cache se necessário
        if self.metadata['total_size'] > self.max_cache_size:
            self._evict_old_entries()
        
        self._save_metadata()
    
    def invalidate(self, key: str):
        """
        Invalida entrada do cache.
        
        Args:
            key: Chave a invalidar
        """
        if key in self.metadata['entries']:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                file_size = cache_file.stat().st_size
                cache_file.unlink()
                self.metadata['total_size'] -= file_size
            
            del self.metadata['entries'][key]
            self._save_metadata()
    
    def _evict_old_entries(self):
        """Remove entradas mais antigas do cache."""
        # Ordenar por timestamp
        sorted_entries = sorted(
            self.metadata['entries'].items(),
            key=lambda x: x[1]['timestamp']
        )
        
        # Remover até atingir 80% do limite
        target_size = self.max_cache_size * 0.8
        
        while self.metadata['total_size'] > target_size and sorted_entries:
            key, _ = sorted_entries.pop(0)
            self.invalidate(key)
        
        logger.info(f"Cache eviction: removidas {len(sorted_entries)} entradas")
    
    def clear(self):
        """Limpa todo o cache."""
        for cache_file in self.cache_dir.glob('*.pkl'):
            cache_file.unlink()
        
        self.metadata = {'entries': {}, 'total_size': 0}
        self._save_metadata()
        
        logger.info("Cache completamente limpo")
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dict com estatísticas
        """
        return {
            'n_entries': len(self.metadata['entries']),
            'total_size_mb': self.metadata['total_size'] / (1024 * 1024),
            'max_size_mb': self.max_cache_size / (1024 * 1024),
            'utilization': self.metadata['total_size'] / self.max_cache_size
        }


class BatchInferenceOptimizer:
    """Otimizador para batch inference."""
    
    @staticmethod
    def prepare_batch(
        student_histories: list,
        candidate_items: list,
        item_to_idx: Dict,
        max_seq_len: int = 200
    ) -> Tuple[Any, Any]:
        """
        Prepara batch otimizado para inferência.
        
        Args:
            student_histories: Lista de históricos
            candidate_items: Lista de candidatos para cada histórico
            item_to_idx: Mapeamento item->idx
            max_seq_len: Comprimento máximo
            
        Returns:
            Tuple com tensors preparados
        """
        import torch
        
        n_items = len(item_to_idx)
        all_inputs = []
        all_masks = []
        
        for history, candidates in zip(student_histories, candidate_items):
            for candidate in candidates:
                # Codificar histórico
                inputs = []
                for interaction in history[-max_seq_len+1:]:
                    item_idx = item_to_idx.get(interaction['item_id'], 0)
                    correct = interaction['correct']
                    input_val = item_idx if correct == 0 else item_idx + n_items
                    inputs.append(input_val)
                
                # Adicionar candidato
                candidate_idx = item_to_idx.get(candidate, 0)
                inputs.append(candidate_idx)
                
                # Padding
                pad_len = max_seq_len - len(inputs)
                if pad_len > 0:
                    inputs.extend([0] * pad_len)
                
                # Mask
                mask = [1] * min(len(inputs), max_seq_len)
                if pad_len > 0:
                    mask.extend([0] * pad_len)
                
                all_inputs.append(inputs[:max_seq_len])
                all_masks.append(mask[:max_seq_len])
        
        return torch.LongTensor(all_inputs), torch.FloatTensor(all_masks)
    
    @staticmethod
    def batch_predict(
        model: Any,
        inputs: Any,
        batch_size: int = 32,
        device: str = 'cpu'
    ) -> Any:
        """
        Executa predições em batch.
        
        Args:
            model: Modelo DKT
            inputs: Tensor de inputs
            batch_size: Tamanho do batch
            device: Dispositivo
            
        Returns:
            Tensor com predições
        """
        import torch
        
        model.eval()
        all_preds = []
        
        n_samples = inputs.shape[0]
        
        with torch.no_grad():
            for i in range(0, n_samples, batch_size):
                batch_inputs = inputs[i:i+batch_size].to(device)
                logits = model(batch_inputs)
                probs = torch.sigmoid(logits)
                all_preds.append(probs.cpu())
        
        return torch.cat(all_preds, dim=0)

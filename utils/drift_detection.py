"""
Sistema de detecção de drift para monitoramento de modelo em produção.

Implementa múltiplos métodos de detecção de drift:
- KS-test para drift de features
- PSI (Population Stability Index)
- Drift de conceito (accuracy drop)
- Alertas automáticos e logging
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detector de drift para modelo DKT."""
    
    def __init__(
        self,
        ks_threshold: float = 0.01,
        psi_threshold: float = 0.2,
        accuracy_drop_threshold: float = 0.1,
        alert_log_path: str = 'results/alerts.log'
    ):
        """
        Inicializa detector de drift.
        
        Args:
            ks_threshold: Threshold para KS-test (p-value)
            psi_threshold: Threshold para PSI
            accuracy_drop_threshold: Threshold para queda de accuracy
            alert_log_path: Caminho do log de alertas
        """
        self.ks_threshold = ks_threshold
        self.psi_threshold = psi_threshold
        self.accuracy_drop_threshold = accuracy_drop_threshold
        self.alert_log_path = Path(alert_log_path)
        self.alert_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.baseline_stats = {}
        
    def compute_psi(
        self,
        baseline: np.ndarray,
        current: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """
        Calcula Population Stability Index (PSI).
        
        Args:
            baseline: Distribuição baseline
            current: Distribuição atual
            n_bins: Número de bins
            
        Returns:
            Valor PSI
        """
        # Criar bins baseados no baseline
        bins = np.linspace(baseline.min(), baseline.max(), n_bins + 1)
        bins[0] = -np.inf
        bins[-1] = np.inf
        
        # Calcular distribuições
        baseline_dist, _ = np.histogram(baseline, bins=bins)
        current_dist, _ = np.histogram(current, bins=bins)
        
        # Normalizar
        baseline_dist = baseline_dist / baseline_dist.sum()
        current_dist = current_dist / current_dist.sum()
        
        # Adicionar epsilon para evitar divisão por zero
        epsilon = 1e-10
        baseline_dist = baseline_dist + epsilon
        current_dist = current_dist + epsilon
        
        # Calcular PSI
        psi = np.sum((current_dist - baseline_dist) * np.log(current_dist / baseline_dist))
        
        return psi
    
    def detect_feature_drift(
        self,
        baseline_data: pd.DataFrame,
        current_data: pd.DataFrame,
        feature_cols: List[str] = ['ability_truth']
    ) -> Dict:
        """
        Detecta drift em features usando KS-test.
        
        Args:
            baseline_data: Dados baseline
            current_data: Dados atuais
            feature_cols: Colunas para verificar drift
            
        Returns:
            Dict com resultados de drift
        """
        drift_results = {
            'timestamp': datetime.now().isoformat(),
            'features': {},
            'has_drift': False
        }
        
        for col in feature_cols:
            if col not in baseline_data.columns or col not in current_data.columns:
                continue
            
            # Remover NaN
            baseline_values = baseline_data[col].dropna().values
            current_values = current_data[col].dropna().values
            
            if len(baseline_values) == 0 or len(current_values) == 0:
                continue
            
            # KS-test
            ks_stat, ks_pvalue = stats.ks_2samp(baseline_values, current_values)
            
            # PSI
            try:
                psi_value = self.compute_psi(baseline_values, current_values)
            except:
                psi_value = None
            
            # Detectar drift
            has_ks_drift = ks_pvalue < self.ks_threshold
            has_psi_drift = psi_value is not None and psi_value > self.psi_threshold
            
            drift_results['features'][col] = {
                'ks_statistic': float(ks_stat),
                'ks_pvalue': float(ks_pvalue),
                'psi': float(psi_value) if psi_value is not None else None,
                'has_ks_drift': has_ks_drift,
                'has_psi_drift': has_psi_drift
            }
            
            if has_ks_drift or has_psi_drift:
                drift_results['has_drift'] = True
        
        return drift_results
    
    def detect_concept_drift(
        self,
        baseline_accuracy: float,
        current_accuracy: float
    ) -> Dict:
        """
        Detecta drift de conceito baseado em queda de accuracy.
        
        Args:
            baseline_accuracy: Accuracy baseline
            current_accuracy: Accuracy atual
            
        Returns:
            Dict com resultados
        """
        accuracy_drop = baseline_accuracy - current_accuracy
        has_drift = accuracy_drop > self.accuracy_drop_threshold
        
        return {
            'timestamp': datetime.now().isoformat(),
            'baseline_accuracy': float(baseline_accuracy),
            'current_accuracy': float(current_accuracy),
            'accuracy_drop': float(accuracy_drop),
            'has_drift': has_drift
        }
    
    def log_alert(self, alert_data: Dict):
        """
        Loga alerta de drift.
        
        Args:
            alert_data: Dados do alerta
        """
        alert_entry = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_data.get('alert_type', 'drift'),
            'details': alert_data
        }
        
        with open(self.alert_log_path, 'a') as f:
            f.write(json.dumps(alert_entry, ensure_ascii=False) + '\n')
        
        logger.warning(f"DRIFT DETECTADO: {alert_data}")
    
    def check_and_alert(
        self,
        baseline_data: pd.DataFrame,
        current_data: pd.DataFrame,
        baseline_accuracy: Optional[float] = None,
        current_accuracy: Optional[float] = None
    ) -> Dict:
        """
        Verifica drift e gera alertas se necessário.
        
        Args:
            baseline_data: Dados baseline
            current_data: Dados atuais
            baseline_accuracy: Accuracy baseline (opcional)
            current_accuracy: Accuracy atual (opcional)
            
        Returns:
            Dict consolidado com resultados
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'feature_drift': None,
            'concept_drift': None,
            'has_any_drift': False
        }
        
        # Verificar feature drift
        feature_drift = self.detect_feature_drift(baseline_data, current_data)
        results['feature_drift'] = feature_drift
        
        if feature_drift['has_drift']:
            results['has_any_drift'] = True
            self.log_alert({
                'alert_type': 'feature_drift',
                'details': feature_drift
            })
        
        # Verificar concept drift
        if baseline_accuracy is not None and current_accuracy is not None:
            concept_drift = self.detect_concept_drift(baseline_accuracy, current_accuracy)
            results['concept_drift'] = concept_drift
            
            if concept_drift['has_drift']:
                results['has_any_drift'] = True
                self.log_alert({
                    'alert_type': 'concept_drift',
                    'details': concept_drift
                })
        
        return results
    
    def save_baseline(self, data: pd.DataFrame, accuracy: float, save_path: str = 'models/drift_baseline.json'):
        """
        Salva baseline para futuras comparações.
        
        Args:
            data: Dados baseline
            accuracy: Accuracy baseline
            save_path: Caminho para salvar
        """
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'accuracy': float(accuracy),
            'n_samples': len(data),
            'ability_stats': {
                'mean': float(data['ability_truth'].mean()) if 'ability_truth' in data.columns else None,
                'std': float(data['ability_truth'].std()) if 'ability_truth' in data.columns else None,
                'min': float(data['ability_truth'].min()) if 'ability_truth' in data.columns else None,
                'max': float(data['ability_truth'].max()) if 'ability_truth' in data.columns else None
            }
        }
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        logger.info(f"Baseline salvo em {save_path}")
    
    def load_baseline(self, load_path: str = 'models/drift_baseline.json') -> Dict:
        """
        Carrega baseline.
        
        Args:
            load_path: Caminho do baseline
            
        Returns:
            Dict com baseline
        """
        with open(load_path) as f:
            baseline = json.load(f)
        
        logger.info(f"Baseline carregado de {load_path}")
        return baseline


def create_drift_report(drift_results: Dict, output_path: str = 'results/drift_report.json'):
    """
    Cria relatório detalhado de drift.
    
    Args:
        drift_results: Resultados de drift
        output_path: Caminho de saída
    """
    report = {
        'generated_at': datetime.now().isoformat(),
        'drift_detected': drift_results.get('has_any_drift', False),
        'summary': drift_results,
        'recommendations': []
    }
    
    if drift_results.get('has_any_drift'):
        report['recommendations'].append('Considere retreinar o modelo com dados recentes')
        report['recommendations'].append('Verifique mudanças na distribuição de dados')
        report['recommendations'].append('Monitore performance do modelo de perto')
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Relatório de drift salvo em {output_path}")

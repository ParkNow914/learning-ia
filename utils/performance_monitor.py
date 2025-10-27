"""
Monitor de Performance em Produção

Sistema completo de monitoramento de performance do modelo em produção,
incluindo métricas, alertas e logging automático.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
from collections import deque


class PerformanceMonitor:
    """
    Monitora performance do sistema em produção.
    
    Features:
    - Rastreamento de latência de inferência
    - Contagem de predições por minuto/hora
    - Monitoramento de uso de memória
    - Detecção de anomalias de performance
    - Alertas automáticos quando thresholds são ultrapassados
    - Logging estruturado de métricas
    """
    
    def __init__(
        self,
        log_dir: str = "results/logs",
        metrics_file: str = "results/performance_metrics.json",
        alert_file: str = "results/performance_alerts.log",
        latency_threshold_ms: float = 500.0,
        throughput_threshold: int = 10,
        window_size: int = 100
    ):
        """
        Inicializa o monitor de performance.
        
        Args:
            log_dir: Diretório para logs
            metrics_file: Arquivo para salvar métricas
            alert_file: Arquivo para alertas
            latency_threshold_ms: Threshold de latência em ms
            throughput_threshold: Mínimo de predições/minuto esperado
            window_size: Tamanho da janela deslizante para métricas
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.alert_file = Path(alert_file)
        
        self.latency_threshold_ms = latency_threshold_ms
        self.throughput_threshold = throughput_threshold
        self.window_size = window_size
        
        # Janelas deslizantes para métricas
        self.latencies = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        self.errors = deque(maxlen=window_size)
        
        # Contadores globais
        self.total_predictions = 0
        self.total_errors = 0
        self.start_time = time.time()
        
        # Configurar logging
        self._setup_logging()
        
        self.logger.info("✅ PerformanceMonitor inicializado")
    
    def _setup_logging(self):
        """Configura sistema de logging estruturado"""
        self.logger = logging.getLogger("PerformanceMonitor")
        self.logger.setLevel(logging.INFO)
        
        # Handler para arquivo JSON-lines
        log_file = self.log_dir / "performance.log"
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        
        # Formato JSON-lines
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_obj = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": record.levelname,
                    "module": "PerformanceMonitor",
                    "message": record.getMessage()
                }
                if hasattr(record, 'extra'):
                    log_obj.update(record.extra)
                return json.dumps(log_obj, ensure_ascii=False)
        
        fh.setFormatter(JSONFormatter())
        self.logger.addHandler(fh)
    
    def record_prediction(
        self,
        latency_ms: float,
        success: bool = True,
        metadata: Optional[Dict] = None
    ):
        """
        Registra uma predição e suas métricas.
        
        Args:
            latency_ms: Latência da predição em milissegundos
            success: Se a predição foi bem-sucedida
            metadata: Metadados adicionais (opcional)
        """
        current_time = time.time()
        
        self.latencies.append(latency_ms)
        self.timestamps.append(current_time)
        self.errors.append(0 if success else 1)
        
        self.total_predictions += 1
        if not success:
            self.total_errors += 1
        
        # Verificar thresholds e alertar se necessário
        self._check_latency_threshold(latency_ms)
        self._check_error_rate()
        
        # Log estruturado
        log_data = {
            "latency_ms": latency_ms,
            "success": success,
            "total_predictions": self.total_predictions,
            "total_errors": self.total_errors
        }
        if metadata:
            log_data.update(metadata)
        
        self.logger.info("Predição registrada", extra=log_data)
    
    def _check_latency_threshold(self, latency_ms: float):
        """Verifica se latência ultrapassou threshold"""
        if latency_ms > self.latency_threshold_ms:
            self._alert(
                f"⚠️ ALERTA: Latência alta detectada: {latency_ms:.2f}ms "
                f"(threshold: {self.latency_threshold_ms}ms)",
                severity="WARNING",
                metric="latency",
                value=latency_ms
            )
    
    def _check_error_rate(self):
        """Verifica taxa de erro"""
        if len(self.errors) >= 10:  # Mínimo de amostras
            error_rate = sum(self.errors) / len(self.errors)
            if error_rate > 0.1:  # >10% de erros
                self._alert(
                    f"⚠️ ALERTA: Taxa de erro elevada: {error_rate:.1%}",
                    severity="ERROR",
                    metric="error_rate",
                    value=error_rate
                )
    
    def _alert(
        self,
        message: str,
        severity: str = "WARNING",
        metric: str = "",
        value: float = 0.0
    ):
        """
        Registra um alerta de performance.
        
        Args:
            message: Mensagem do alerta
            severity: Severidade (INFO, WARNING, ERROR, CRITICAL)
            metric: Nome da métrica que gerou o alerta
            value: Valor da métrica
        """
        alert_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": severity,
            "metric": metric,
            "value": value,
            "message": message
        }
        
        # Salvar alerta
        with open(self.alert_file, "a") as f:
            f.write(json.dumps(alert_data, ensure_ascii=False) + "\n")
        
        # Log também
        if severity == "CRITICAL":
            self.logger.critical(message, extra=alert_data)
        elif severity == "ERROR":
            self.logger.error(message, extra=alert_data)
        else:
            self.logger.warning(message, extra=alert_data)
    
    def get_current_metrics(self) -> Dict:
        """
        Retorna métricas atuais do sistema.
        
        Returns:
            Dict com métricas de performance
        """
        uptime = time.time() - self.start_time
        
        metrics = {
            "uptime_seconds": uptime,
            "total_predictions": self.total_predictions,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / max(self.total_predictions, 1),
            "predictions_per_second": self.total_predictions / max(uptime, 1)
        }
        
        # Métricas da janela atual
        if self.latencies:
            metrics["latency_avg_ms"] = sum(self.latencies) / len(self.latencies)
            metrics["latency_p50_ms"] = sorted(self.latencies)[len(self.latencies) // 2]
            metrics["latency_p95_ms"] = sorted(self.latencies)[int(len(self.latencies) * 0.95)]
            metrics["latency_p99_ms"] = sorted(self.latencies)[int(len(self.latencies) * 0.99)]
            metrics["latency_max_ms"] = max(self.latencies)
        
        # Throughput na última minuto
        if len(self.timestamps) >= 2:
            recent_window = 60  # 1 minuto
            recent_count = sum(
                1 for t in self.timestamps
                if time.time() - t <= recent_window
            )
            metrics["throughput_per_minute"] = recent_count
            
            if recent_count < self.throughput_threshold:
                self._alert(
                    f"⚠️ ALERTA: Throughput baixo: {recent_count} pred/min "
                    f"(esperado: >= {self.throughput_threshold})",
                    severity="WARNING",
                    metric="throughput",
                    value=recent_count
                )
        
        return metrics
    
    def save_metrics(self):
        """Salva métricas atuais em arquivo JSON"""
        metrics = self.get_current_metrics()
        metrics["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        with open(self.metrics_file, "w") as f:
            json.dumps(metrics, f, indent=2, ensure_ascii=False)
        
        self.logger.info("Métricas salvas", extra=metrics)
    
    def generate_report(self) -> str:
        """
        Gera relatório de performance formatado.
        
        Returns:
            String com relatório formatado
        """
        metrics = self.get_current_metrics()
        
        report = [
            "=" * 60,
            "  📊 RELATÓRIO DE PERFORMANCE EM PRODUÇÃO",
            "=" * 60,
            "",
            f"⏱️  Uptime: {metrics['uptime_seconds']:.0f}s ({metrics['uptime_seconds']/3600:.1f}h)",
            f"📈 Total de Predições: {metrics['total_predictions']}",
            f"❌ Total de Erros: {metrics['total_errors']}",
            f"📊 Taxa de Erro: {metrics['error_rate']:.2%}",
            f"⚡ Predições/segundo: {metrics['predictions_per_second']:.2f}",
            ""
        ]
        
        if "latency_avg_ms" in metrics:
            report.extend([
                "🕐 Latência (ms):",
                f"   Média: {metrics['latency_avg_ms']:.2f}ms",
                f"   P50: {metrics['latency_p50_ms']:.2f}ms",
                f"   P95: {metrics['latency_p95_ms']:.2f}ms",
                f"   P99: {metrics['latency_p99_ms']:.2f}ms",
                f"   Max: {metrics['latency_max_ms']:.2f}ms",
                ""
            ])
        
        if "throughput_per_minute" in metrics:
            report.append(f"📊 Throughput (última minuto): {metrics['throughput_per_minute']} pred/min")
            report.append("")
        
        # Status de saúde
        health_status = "✅ SAUDÁVEL"
        if metrics["error_rate"] > 0.1:
            health_status = "⚠️ ATENÇÃO - Taxa de erro elevada"
        if "latency_avg_ms" in metrics and metrics["latency_avg_ms"] > self.latency_threshold_ms:
            health_status = "⚠️ ATENÇÃO - Latência alta"
        
        report.extend([
            f"🏥 Status de Saúde: {health_status}",
            "=" * 60
        ])
        
        return "\n".join(report)
    
    def reset_metrics(self):
        """Reseta todas as métricas (útil para testes)"""
        self.latencies.clear()
        self.timestamps.clear()
        self.errors.clear()
        self.total_predictions = 0
        self.total_errors = 0
        self.start_time = time.time()
        
        self.logger.info("📊 Métricas resetadas")


# Funções auxiliares para uso simples
_global_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """Retorna instância global do monitor (singleton)"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def record_prediction(latency_ms: float, success: bool = True, **kwargs):
    """
    Atalho para registrar predição no monitor global.
    
    Args:
        latency_ms: Latência em milissegundos
        success: Se foi bem-sucedida
        **kwargs: Metadados adicionais
    """
    monitor = get_monitor()
    monitor.record_prediction(latency_ms, success, kwargs if kwargs else None)


def get_current_metrics() -> Dict:
    """Retorna métricas atuais do monitor global"""
    return get_monitor().get_current_metrics()


def generate_report() -> str:
    """Gera relatório do monitor global"""
    return get_monitor().generate_report()


if __name__ == "__main__":
    # Exemplo de uso
    print("🧪 Testando PerformanceMonitor...")
    
    monitor = PerformanceMonitor(
        latency_threshold_ms=100.0,
        throughput_threshold=5
    )
    
    # Simular predições
    import random
    for i in range(50):
        latency = random.uniform(50, 150)
        success = random.random() > 0.05  # 95% de sucesso
        monitor.record_prediction(latency, success)
        time.sleep(0.1)
    
    # Gerar relatório
    print(monitor.generate_report())
    
    # Salvar métricas
    monitor.save_metrics()
    
    print("\n✅ Teste concluído!")
    print(f"📊 Métricas salvas em: {monitor.metrics_file}")
    print(f"📋 Logs em: {monitor.log_dir}/performance.log")

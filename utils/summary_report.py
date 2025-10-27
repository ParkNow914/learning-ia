"""Gera relatório resumido."""
import json
from pathlib import Path
from datetime import datetime

def generate_summary():
    """Gera results/demo_summary.txt."""
    try:
        with open('data/sources.json') as f:
            sources = json.load(f)
        with open('results/stats.json') as f:
            stats = json.load(f)
        with open('results/summary.json') as f:
            summary = json.load(f)
    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")
        return
    
    report = f"""
{'='*70}
RELATÓRIO DO SISTEMA KNOWLEDGE TRACING
{'='*70}
Gerado em: {datetime.now().isoformat()}

DATASETS UTILIZADOS:
"""
    for source in sources:
        report += f"  - {source['name']}: {source['license']}\n"
    
    report += f"""
ESTATÍSTICAS DOS DADOS:
  • Estudantes: {stats['n_students']}
  • Itens: {stats['n_items']}
  • Interações: {stats['n_interactions']}
  • Taxa de acerto: {stats['correct_rate']:.2%}

MÉTRICAS DO MODELO:
  • AUC: {summary['auc_dkt']:.4f}
  • Accuracy: {summary['accuracy_dkt']:.4f}
  • Ganho médio (DKT): {summary['avg_gain_dkt']:.4f}

ARQUIVOS PRINCIPAIS:
  • Modelo: models/dkt.pt
  • Métricas: results/summary.json
  • Figuras: results/figures/
  • Logs: results/logs/

{'='*70}
"""
    
    Path('results/demo_summary.txt').write_text(report)
    print("✓ Relatório salvo em results/demo_summary.txt")
    print(report)

if __name__ == '__main__':
    generate_summary()

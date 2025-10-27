"""
Script para treinar o modelo DKT.

Uso:
    python train_dkt.py --epochs 5 --batch-size 32 --lr 5e-4 --seed 42
"""

import argparse
import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split

from dkt_model import (
    DKTModel, build_dataset_from_csv, collate_fn,
    train_epoch, evaluate, save_model
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","message":"%(message)s"}',
    handlers=[
        logging.FileHandler("results/logs/train.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def set_seed(seed: int):
    """Configura seed para reproducibilidade."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def plot_metrics(train_losses, val_losses, val_aucs, save_dir):
    """Plota métricas de treino."""
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Plot loss
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_dir / 'loss.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Plot AUC
    plt.figure(figsize=(10, 5))
    plt.plot(val_aucs, label='Val AUC', color='green')
    plt.xlabel('Epoch')
    plt.ylabel('AUC')
    plt.title('Validation AUC')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_dir / 'auc.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Gráficos salvos em {save_dir}")


def main():
    parser = argparse.ArgumentParser(description='Treinar modelo DKT')
    parser.add_argument('--data-csv', type=str, default='data/real_combined_dataset.csv',
                        help='Caminho do CSV de dados')
    parser.add_argument('--epochs', type=int, default=5,
                        help='Número de épocas')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Tamanho do batch')
    parser.add_argument('--lr', type=float, default=5e-4,
                        help='Learning rate')
    parser.add_argument('--hidden-size', type=int, default=128,
                        help='Tamanho da camada oculta')
    parser.add_argument('--n-layers', type=int, default=2,
                        help='Número de camadas LSTM')
    parser.add_argument('--dropout', type=float, default=0.2,
                        help='Taxa de dropout')
    parser.add_argument('--max-seq-len', type=int, default=200,
                        help='Comprimento máximo da sequência')
    parser.add_argument('--device', type=str, default='cpu',
                        help='Dispositivo (cpu ou cuda)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Seed para reproducibilidade')
    parser.add_argument('--save-dir', type=str, default='models',
                        help='Diretório para salvar modelo')
    parser.add_argument('--resume', type=str, default=None,
                        help='Caminho de checkpoint para retomar treino')
    parser.add_argument('--val-split', type=float, default=0.2,
                        help='Proporção de dados para validação')
    
    args = parser.parse_args()
    
    # Configurar seed
    set_seed(args.seed)
    
    # Criar diretórios
    Path('results/logs').mkdir(parents=True, exist_ok=True)
    Path('results/figures').mkdir(parents=True, exist_ok=True)
    Path(args.save_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("Iniciando treino do modelo DKT")
    logger.info(f"Configurações: {vars(args)}")
    
    # Carregar dados
    dataset, item_to_idx, metadata = build_dataset_from_csv(
        args.data_csv,
        max_seq_len=args.max_seq_len
    )
    
    # Split train/val
    val_size = int(len(dataset) * args.val_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(
        dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(args.seed)
    )
    
    logger.info(f"Train size: {len(train_dataset)}, Val size: {len(val_dataset)}")
    
    # DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collate_fn
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collate_fn
    )
    
    # Criar modelo
    n_items = metadata['n_items']
    model = DKTModel(
        n_items=n_items,
        hidden_size=args.hidden_size,
        n_layers=args.n_layers,
        dropout=args.dropout
    )
    model.to(args.device)
    
    logger.info(f"Modelo criado: {sum(p.numel() for p in model.parameters())} parâmetros")
    
    # Otimizador e loss
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=2
    )
    
    # Treinar
    best_val_loss = float('inf')
    patience_counter = 0
    max_patience = 5
    
    train_losses = []
    val_losses = []
    val_aucs = []
    
    train_log = []
    
    for epoch in range(args.epochs):
        logger.info(f"\n{'='*60}")
        logger.info(f"Época {epoch + 1}/{args.epochs}")
        logger.info(f"{'='*60}")
        
        # Treinar
        train_loss = train_epoch(model, train_loader, optimizer, criterion, args.device)
        logger.info(f"Train Loss: {train_loss:.4f}")
        
        # Avaliar
        val_metrics = evaluate(model, val_loader, criterion, args.device)
        logger.info(f"Val Loss: {val_metrics['loss']:.4f}")
        logger.info(f"Val AUC: {val_metrics['auc']:.4f}")
        logger.info(f"Val Accuracy: {val_metrics['accuracy']:.4f}")
        logger.info(f"Val MAE: {val_metrics['mae']:.4f}")
        
        # Registrar
        train_losses.append(train_loss)
        val_losses.append(val_metrics['loss'])
        val_aucs.append(val_metrics['auc'])
        
        train_log.append({
            'epoch': epoch + 1,
            'train_loss': train_loss,
            'val_loss': val_metrics['loss'],
            'val_auc': val_metrics['auc'],
            'val_accuracy': val_metrics['accuracy'],
            'val_mae': val_metrics['mae']
        })
        
        # Scheduler
        scheduler.step(val_metrics['loss'])
        
        # Early stopping
        if val_metrics['loss'] < best_val_loss:
            best_val_loss = val_metrics['loss']
            patience_counter = 0
            
            # Salvar melhor modelo
            model_metadata = {
                'version': 'v1.0.0',
                'timestamp_iso': datetime.now().isoformat(),
                'val_auc': val_metrics['auc'],
                'val_loss': best_val_loss,
                'train_params': vars(args),
                'item_to_idx': item_to_idx
            }
            
            save_model(model, f"{args.save_dir}/dkt.pt", model_metadata)
            logger.info("✓ Melhor modelo salvo")
        else:
            patience_counter += 1
            logger.info(f"Paciência: {patience_counter}/{max_patience}")
            
            if patience_counter >= max_patience:
                logger.info("Early stopping acionado")
                break
    
    # Salvar log de treino
    import pandas as pd
    log_df = pd.DataFrame(train_log)
    log_df.to_csv('results/train_log.csv', index=False)
    logger.info("Log de treino salvo em results/train_log.csv")
    
    # Plotar métricas
    plot_metrics(train_losses, val_losses, val_aucs, 'results/figures')
    
    logger.info("\n" + "="*60)
    logger.info("Treino concluído!")
    logger.info(f"Melhor Val Loss: {best_val_loss:.4f}")
    logger.info(f"Melhor Val AUC: {max(val_aucs):.4f}")
    logger.info(f"Modelo salvo em: {args.save_dir}/dkt.pt")
    logger.info("="*60)


if __name__ == '__main__':
    main()

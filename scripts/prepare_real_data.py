"""Script para preparar dados customizados."""
import argparse
import json
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--mapping', default=None)
    parser.add_argument('--anonymize', action='store_true')
    parser.add_argument('--output', default='data/custom_dataset.csv')
    args = parser.parse_args()
    
    df = pd.read_csv(args.input)
    
    if args.mapping:
        with open(args.mapping) as f:
            mapping = json.load(f)
        df = df.rename(columns=mapping)
    
    required = ['student_id', 'timestamp', 'item_id', 'skill_id', 'correct']
    if not all(col in df.columns for col in required):
        print(f"Erro: Colunas necessárias: {required}")
        return
    
    df.to_csv(args.output, index=False)
    print(f"✓ Dataset salvo em {args.output}")

if __name__ == '__main__':
    main()

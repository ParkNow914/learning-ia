#!/usr/bin/env python3
"""
Script para verificar se todas as dependências estão instaladas corretamente.

Uso:
    python check_installation.py
"""

import sys
from importlib import import_module


def check_package(package_name, import_name=None):
    """Verifica se um pacote está instalado."""
    if import_name is None:
        import_name = package_name

    try:
        import_module(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - NÃO INSTALADO")
        return False


def main():
    """Verifica instalação de todas as dependências."""
    print("=" * 60)
    print("VERIFICAÇÃO DE INSTALAÇÃO - Knowledge Tracing")
    print("=" * 60)

    required_packages = [
        ("torch", "torch"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("pytest", "pytest"),
        ("requests", "requests"),
        ("tqdm", "tqdm"),
        ("python-dotenv", "dotenv"),
    ]

    print("\nVerificando pacotes Python:")
    print("-" * 60)

    all_ok = True
    for package_name, import_name in required_packages:
        if not check_package(package_name, import_name):
            all_ok = False

    print("-" * 60)

    if all_ok:
        print("\n✅ Todas as dependências estão instaladas!")
        print("\nPróximos passos:")
        print("  1. Execute: python data/data_fetch_and_prepare.py")
        print("  2. Execute: python train_dkt.py --epochs 3")
        print("  3. Execute: python evaluate_policies.py --episodes 100")
        print("  Ou simplesmente: ./demo_run.sh")
    else:
        print("\n❌ Algumas dependências estão faltando!")
        print("\nPara instalar todas as dependências:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    print("\nPython:", sys.version)
    print("=" * 60)


if __name__ == "__main__":
    main()

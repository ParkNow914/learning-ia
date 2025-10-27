#!/usr/bin/env python3
"""
Script de validação completa do sistema Knowledge Tracing.
Verifica todos os componentes, testa funcionalidades e gera relatório.
"""

import sys
import subprocess
from pathlib import Path


def print_section(title):
    """Imprime cabeçalho de seção."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def run_command(cmd, description):
    """Executa comando e retorna resultado."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"❌ {description} - FALHOU")
            if result.stderr:
                print(f"   Erro: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - Exceção: {str(e)[:100]}")
        return False


def check_imports():
    """Verifica se todos os módulos importam corretamente."""
    print_section("VERIFICANDO IMPORTS")
    
    modules = [
        "dkt_model",
        "dkt_model_advanced",
        "recommender",
        "train_dkt",
        "evaluate_policies",
        "utils.calibration",
        "utils.drift_detection",
        "utils.optimization",
        "utils.data_augmentation",
        "utils.hyperparam_search",
        "app.main",
    ]
    
    success = 0
    for module in modules:
        if run_command(f"python3 -c 'import {module}'", f"Import {module}"):
            success += 1
    
    print(f"\n📊 Imports: {success}/{len(modules)} OK")
    return success == len(modules)


def check_syntax():
    """Verifica sintaxe de todos os arquivos Python."""
    print_section("VERIFICANDO SINTAXE")
    
    cmd = "python3 -m py_compile *.py utils/*.py app/*.py scripts/*.py tests/*.py 2>&1"
    return run_command(cmd, "Compilação de sintaxe")


def run_tests():
    """Executa suite de testes."""
    print_section("EXECUTANDO TESTES")
    
    cmd = "python3 -m pytest tests/ -v --tb=short"
    return run_command(cmd, "Suite de testes pytest")


def check_linting():
    """Verifica qualidade do código."""
    print_section("VERIFICANDO QUALIDADE DO CÓDIGO")
    
    # Instalar flake8 se necessário
    subprocess.run("python3 -m pip install --quiet flake8 2>/dev/null", shell=True)
    
    cmd = "python3 -m flake8 --max-line-length=120 --extend-ignore=E203,W503,E501 app/main.py check_installation.py"
    return run_command(cmd, "Linting com flake8")


def check_api():
    """Verifica se API pode ser carregada."""
    print_section("VERIFICANDO API")
    
    cmd = "python3 -c 'from app.main import app; print(len(app.routes))'"
    return run_command(cmd, "Carregamento da API FastAPI")


def check_dependencies():
    """Verifica dependências instaladas."""
    print_section("VERIFICANDO DEPENDÊNCIAS")
    
    return run_command("python3 check_installation.py", "Verificação de dependências")


def generate_report():
    """Gera relatório final."""
    print_section("RELATÓRIO FINAL")
    
    report = {
        "imports": check_imports(),
        "syntax": check_syntax(),
        "tests": run_tests(),
        "linting": check_linting(),
        "api": check_api(),
    }
    
    print("\n" + "="*60)
    print("  📋 RESUMO DA VALIDAÇÃO")
    print("="*60 + "\n")
    
    total = len(report)
    passed = sum(report.values())
    
    for check, status in report.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check.upper()}: {'PASSOU' if status else 'FALHOU'}")
    
    print("\n" + "-"*60)
    print(f"📊 Total: {passed}/{total} verificações passaram")
    print("-"*60 + "\n")
    
    if passed == total:
        print("🎉 SISTEMA 100% VALIDADO E FUNCIONANDO!")
        print("✅ Todos os componentes estão operacionais")
        print("✅ Código está livre de erros")
        print("✅ Testes estão passando")
        print("✅ Qualidade do código verificada")
        print("\n🚀 Sistema pronto para uso!")
        return 0
    else:
        print("⚠️  ALGUNS PROBLEMAS ENCONTRADOS")
        print(f"❌ {total - passed} verificação(ões) falharam")
        print("\n💡 Consulte as mensagens acima para mais detalhes")
        return 1


def main():
    """Função principal."""
    print("\n" + "="*60)
    print("  🧪 VALIDAÇÃO COMPLETA DO SISTEMA KNOWLEDGE TRACING")
    print("="*60)
    
    exit_code = generate_report()
    
    print("\n" + "="*60)
    print(f"  Validação concluída! Código de saída: {exit_code}")
    print("="*60 + "\n")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

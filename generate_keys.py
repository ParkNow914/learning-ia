#!/usr/bin/env python3
"""
Gerador de chaves seguras para configuração do sistema.

Uso:
    python generate_keys.py

Gera:
    - SECRET_API_KEY: Chave de autenticação da API
    - SALT_ANON: Salt para anonimização de dados
"""

import secrets


def generate_secure_key(length: int = 32) -> str:
    """
    Gera uma chave segura usando secrets.token_urlsafe().
    
    Args:
        length: Tamanho da chave em bytes (padrão: 32)
        
    Returns:
        String com chave segura URL-safe
    """
    return secrets.token_urlsafe(length)


def generate_hex_key(length: int = 32) -> str:
    """
    Gera uma chave hexadecimal segura.
    
    Args:
        length: Tamanho da chave em bytes (padrão: 32)
        
    Returns:
        String hexadecimal
    """
    return secrets.token_hex(length)


def main():
    """Gera e exibe chaves seguras para configuração."""
    print("=" * 70)
    print("Gerador de Chaves Seguras - learning-ia")
    print("=" * 70)
    print()
    
    # Gerar chaves
    api_key = generate_secure_key(32)
    salt_anon = generate_secure_key(32)
    hex_key = generate_hex_key(16)
    
    print("✅ Chaves geradas com sucesso!")
    print()
    print("Copie e cole no seu arquivo .env:")
    print("-" * 70)
    print()
    print(f"SECRET_API_KEY={api_key}")
    print(f"SALT_ANON={salt_anon}")
    print()
    print("-" * 70)
    print()
    print("💡 Dicas de Segurança:")
    print("  • Nunca compartilhe estas chaves publicamente")
    print("  • Nunca faça commit do arquivo .env")
    print("  • Use chaves diferentes para cada ambiente (dev/staging/prod)")
    print("  • Guarde as chaves de produção em um gerenciador de secrets")
    print()
    print("🔐 Chave Hexadecimal (alternativa):")
    print(f"   {hex_key}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()

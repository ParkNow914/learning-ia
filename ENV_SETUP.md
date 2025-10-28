# 🔧 Guia de Configuração do Ambiente

Este guia explica como configurar as variáveis de ambiente do sistema learning-ia.

---

## 🚀 Quick Start

### 1. Copiar arquivo de exemplo

```bash
cp .env.example .env
```

### 2. Gerar chaves seguras

```bash
python generate_keys.py
```

Copie as chaves geradas para o arquivo `.env`.

### 3. Editar configurações

Abra `.env` e ajuste conforme necessário:

```bash
nano .env
# ou
vim .env
# ou use seu editor favorito
```

---

## 📝 Variáveis Obrigatórias

### SECRET_API_KEY
**Descrição**: Chave de autenticação da API  
**Padrão**: `troque_aqui_por_uma_chave_segura_minimo_32_caracteres`  
**Exemplo**: `8sKnE_vQ9x4hT2mL6pB3nF7wR1cX5jY0`

⚠️ **IMPORTANTE**: Troque por uma chave segura e aleatória!

```bash
# Gerar com Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Ou use o script
python generate_keys.py
```

### SALT_ANON
**Descrição**: Salt para anonimização de dados sensíveis  
**Padrão**: `troque_este_salt_por_algo_unico_minimo_32_caracteres`  
**Exemplo**: `aZ9xM2nK5qW8tY3vL7pR0bC4jF6hG1sD`

⚠️ **IMPORTANTE**: Use um valor único e diferente da API key!

---

## ⚙️ Variáveis Opcionais

### Rate Limiting

```bash
# Máximo de requisições por minuto por IP
RATE_LIMIT_PER_MIN=60
```

### Redis (Opcional)

```bash
# URL do Redis para rate limiting e cache persistente
# Deixe vazio para usar fallback in-memory
REDIS_URL=redis://localhost:6379

# Com senha
REDIS_URL=redis://:senha@localhost:6379
```

### Ambiente

```bash
# development, staging, ou production
ENVIRONMENT=development

# Ativar modo debug (desative em produção!)
DEBUG=true

# Nível de log: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

### CORS

```bash
# Origens permitidas (separadas por vírgula)
# Use * apenas em desenvolvimento!
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Em produção
ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
```

### Modelo

```bash
# Seed para reprodutibilidade
SEED=42

# Comprimento máximo de sequência
MAX_SEQ_LEN=200

# Caminho do modelo
MODEL_PATH=models/dkt.pt
```

### Upload

```bash
# Tamanho máximo de upload em MB
MAX_UPLOAD_SIZE_MB=50
```

### Monitoramento

```bash
# Ativar endpoint de métricas Prometheus
ENABLE_METRICS=false

# Sentry DSN para rastreamento de erros (opcional)
# SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## 🔒 Segurança em Produção

### ✅ Checklist de Segurança

- [ ] Trocar `SECRET_API_KEY` por valor aleatório e forte
- [ ] Trocar `SALT_ANON` por valor aleatório e único
- [ ] Configurar `ALLOWED_ORIGINS` com domínios específicos (não usar `*`)
- [ ] Desativar `DEBUG` (definir como `false`)
- [ ] Configurar `LOG_LEVEL` como `INFO` ou `WARNING`
- [ ] Adicionar `.env` ao `.gitignore`
- [ ] Usar Redis para rate limiting persistente
- [ ] Configurar HTTPS no servidor
- [ ] Usar gerenciador de secrets (AWS Secrets Manager, Vault, etc.)

### 🔐 Gerenciamento de Secrets

#### AWS Secrets Manager

```bash
# Armazenar secret
aws secretsmanager create-secret \
    --name learning-ia/api-key \
    --secret-string "sua_chave_aqui"

# Recuperar secret
aws secretsmanager get-secret-value \
    --secret-id learning-ia/api-key \
    --query SecretString \
    --output text
```

#### HashiCorp Vault

```bash
# Armazenar
vault kv put secret/learning-ia \
    api_key="sua_chave" \
    salt="seu_salt"

# Recuperar
vault kv get secret/learning-ia
```

#### Docker Secrets

```bash
# Criar secret
echo "sua_chave" | docker secret create api_key -

# Usar no docker-compose.yml
secrets:
  api_key:
    external: true
```

---

## 📋 Exemplos por Ambiente

### Desenvolvimento

```bash
SECRET_API_KEY=dev_key_apenas_para_testes_locais_123456789
SALT_ANON=dev_salt_apenas_para_testes_locais_987654321
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=*
REDIS_URL=
```

### Staging

```bash
SECRET_API_KEY=gerar_com_secrets.token_urlsafe_32
SALT_ANON=gerar_com_secrets.token_urlsafe_32
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://staging.seu-dominio.com
REDIS_URL=redis://redis-staging:6379
```

### Produção

```bash
SECRET_API_KEY=usar_secrets_manager_ou_vault
SALT_ANON=usar_secrets_manager_ou_vault
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
REDIS_URL=redis://:senha_segura@redis-prod:6379
ENABLE_METRICS=true
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## 🧪 Validação

### Verificar Configuração

```bash
# Testar se .env está configurado
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('API Key:', 'OK' if os.getenv('SECRET_API_KEY') else 'FALTANDO')"

# Ou use o script de validação
python check_installation.py
```

### Testar API Key

```bash
# Com curl
curl -H "x-api-key: sua_chave" http://localhost:8000/health

# Deve retornar 200 OK
```

---

## ❓ Troubleshooting

### Problema: API retorna 401 Unauthorized

**Causa**: API key incorreta ou ausente

**Solução**:
```bash
# Verificar se .env existe e tem SECRET_API_KEY
cat .env | grep SECRET_API_KEY

# Testar com a chave correta
export API_KEY=$(grep SECRET_API_KEY .env | cut -d '=' -f2)
curl -H "x-api-key: $API_KEY" http://localhost:8000/health
```

### Problema: CORS error no frontend

**Causa**: `ALLOWED_ORIGINS` não inclui origem do frontend

**Solução**:
```bash
# Adicionar origem ao .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Problema: Redis não conecta

**Causa**: `REDIS_URL` incorreto ou Redis não está rodando

**Solução**:
```bash
# Verificar se Redis está rodando
redis-cli ping

# Ou com Docker
docker-compose ps redis

# Testar conexão
redis-cli -u redis://localhost:6379 ping
```

---

## 📚 Recursos

- [12-Factor App - Config](https://12factor.net/config)
- [OWASP - Configuration](https://owasp.org/www-project-top-ten/)
- [FastAPI - Settings](https://fastapi.tiangolo.com/advanced/settings/)
- [Python Secrets](https://docs.python.org/3/library/secrets.html)

---

**✨ Configuração segura = Aplicação segura!**

**Última Atualização**: 2025-10-28  
**Versão**: 1.0.0

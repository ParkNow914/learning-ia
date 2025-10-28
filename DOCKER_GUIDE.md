# 🐳 Guia Docker - learning-ia

**Desenvolvimento simplificado com Docker Compose**

---

## 🚀 Quick Start

### Opção 1: Docker Compose (Recomendado)

```bash
# 1. Clonar repositório
git clone https://github.com/ParkNow914/learning-ia.git
cd learning-ia

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves

# 3. Iniciar todos os serviços
make docker-up

# Ou diretamente:
docker-compose up -d
```

**Pronto!** 🎉
- API: http://localhost:8000
- Frontend: http://localhost:8080
- Redis: localhost:6379

---

## 📋 Serviços Incluídos

### 1. API (FastAPI)
- **Porta**: 8000
- **Container**: learning-ia-api
- **Features**:
  - Auto-reload em desenvolvimento
  - Volumes montados para hot-reload
  - Health check automático

### 2. Redis
- **Porta**: 6379
- **Container**: learning-ia-redis
- **Features**:
  - Persistência de dados (appendonly)
  - Health check integrado
  - Volume para dados persistentes

### 3. Frontend (Nginx)
- **Porta**: 8080
- **Container**: learning-ia-frontend
- **Features**:
  - Serve arquivos estáticos
  - Nginx Alpine (leve e rápido)

---

## 🛠️ Comandos Úteis

### Gerenciamento de Serviços

```bash
# Iniciar serviços
make docker-up
# ou
docker-compose up -d

# Parar serviços
make docker-down
# ou
docker-compose down

# Reiniciar serviços
make docker-restart
# ou
docker-compose restart

# Ver logs
make docker-logs
# ou
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f api
docker-compose logs -f redis
```

### Build e Desenvolvimento

```bash
# Build das imagens
make docker-build
# ou
docker-compose build

# Build sem cache
docker-compose build --no-cache

# Rebuild e restart
docker-compose up -d --build
```

### Manutenção

```bash
# Entrar no container da API
make docker-shell
# ou
docker-compose exec api /bin/bash

# Executar comando no container
docker-compose exec api python train_dkt.py --epochs 3

# Limpar recursos
make docker-clean
# ou
docker-compose down -v
docker system prune -f
```

---

## 🔧 Configuração

### Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

```bash
# API Security
SECRET_API_KEY=your_secure_api_key_here
SALT_ANON=your_secure_salt_here

# Rate Limiting
RATE_LIMIT_PER_MIN=60

# Redis
REDIS_URL=redis://redis:6379
```

### Volumes

Os seguintes diretórios são montados como volumes:

```yaml
volumes:
  - ./data:/app/data           # Dados de treino
  - ./models:/app/models       # Modelos salvos
  - ./results:/app/results     # Resultados e logs
  - ./uploads:/app/uploads     # Uploads temporários
```

**Benefícios**:
- ✅ Dados persistem entre restarts
- ✅ Hot-reload durante desenvolvimento
- ✅ Fácil acesso aos arquivos do host

---

## 📊 Monitoramento

### Health Checks

Todos os serviços têm health checks automáticos:

```bash
# Verificar status
docker-compose ps

# Ver health do Redis
docker-compose exec redis redis-cli ping

# Ver health da API
curl http://localhost:8000/health
```

### Logs Estruturados

```bash
# Logs em tempo real
docker-compose logs -f

# Últimas 100 linhas
docker-compose logs --tail=100

# Logs de um serviço
docker-compose logs -f api

# Logs com timestamp
docker-compose logs -f --timestamps
```

---

## 🚀 Workflow de Desenvolvimento

### 1. Desenvolvimento Local

```bash
# Iniciar serviços
make docker-up

# Logs em tempo real em outro terminal
make docker-logs

# Fazer mudanças no código
# (API recarrega automaticamente)

# Executar testes
docker-compose exec api pytest tests/ -v

# Parar quando terminar
make docker-down
```

### 2. Treinar Modelo

```bash
# Dentro do container
make docker-shell

# Ou executar diretamente
docker-compose exec api python data/data_fetch_and_prepare.py --datasets assistments
docker-compose exec api python train_dkt.py --epochs 5
```

### 3. Testar API

```bash
# Health check
curl http://localhost:8000/health

# Métricas (com API key)
curl -H "x-api-key: your_key" http://localhost:8000/metrics

# Upload CSV
curl -X POST \
  -H "x-api-key: your_key" \
  -F "file=@data/real_combined_dataset.csv" \
  http://localhost:8000/upload-csv
```

---

## 🐛 Troubleshooting

### Problema: Porta já em uso

```bash
# Erro: "port is already allocated"

# Solução 1: Mudar porta no docker-compose.yml
# Trocar "8000:8000" para "8001:8000"

# Solução 2: Parar processo na porta
lsof -ti:8000 | xargs kill -9
```

### Problema: Permissões de arquivo

```bash
# Erro: "Permission denied"

# Solução: Ajustar permissões
sudo chown -R $USER:$USER data/ models/ results/
```

### Problema: Container não inicia

```bash
# Ver logs detalhados
docker-compose logs api

# Rebuild sem cache
docker-compose build --no-cache api
docker-compose up -d
```

### Problema: Redis não conecta

```bash
# Verificar se Redis está rodando
docker-compose ps

# Testar conexão
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

---

## 📦 Produção

### Build para Produção

```bash
# Build otimizado
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Sem auto-reload
docker-compose -f docker-compose.prod.yml up -d
```

### docker-compose.prod.yml (criar)

```yaml
version: '3.8'

services:
  api:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    restart: always
    environment:
      - SECRET_API_KEY=${SECRET_API_KEY}
      - REDIS_URL=redis://redis:6379

  redis:
    restart: always
```

### Backup de Dados

```bash
# Backup do Redis
docker-compose exec redis redis-cli BGSAVE

# Backup de volumes
docker run --rm -v learning-ia_redis_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

---

## 🎯 Melhores Práticas

### Segurança

1. **Nunca commitar .env**
   ```bash
   # Verificar
   cat .gitignore | grep .env
   ```

2. **Usar secrets em produção**
   ```bash
   docker secret create api_key api_key.txt
   ```

3. **Limitar recursos**
   ```yaml
   services:
     api:
       deploy:
         resources:
           limits:
             cpus: '0.5'
             memory: 512M
   ```

### Performance

1. **Multi-stage builds** (já implementado no Dockerfile)
2. **Cache de layers**: Copiar requirements.txt primeiro
3. **Imagens slim**: Usar python:3.10-slim

### Monitoramento

1. **Health checks**: Sempre configurar
2. **Logging**: Usar JSON structured logs
3. **Metrics**: Exportar para Prometheus (futuro)

---

## 🔗 Links Úteis

- **Docker Docs**: https://docs.docker.com/
- **Compose Docs**: https://docs.docker.com/compose/
- **FastAPI Docker**: https://fastapi.tiangolo.com/deployment/docker/
- **Redis Docker**: https://hub.docker.com/_/redis

---

## ✅ Checklist de Setup

- [ ] Docker e Docker Compose instalados
- [ ] Arquivo .env configurado
- [ ] Portas 8000, 8080, 6379 disponíveis
- [ ] `make docker-build` executado
- [ ] `make docker-up` executado
- [ ] Health checks passando
- [ ] API respondendo em http://localhost:8000/health
- [ ] Frontend acessível em http://localhost:8080

---

**🐳 Docker simplifica o desenvolvimento! Experimente!**

**Última Atualização**: 2025-10-28  
**Versão Docker**: 1.0.0

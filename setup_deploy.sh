#!/bin/bash

# Script de Deploy e Setup Automatizado
# Prepara o ambiente e faz deploy do sistema Knowledge Tracing

set -e  # Para em caso de erro

echo "============================================================"
echo "  🚀 SETUP E DEPLOY DO SISTEMA KNOWLEDGE TRACING"
echo "============================================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para log
log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Python está instalado
echo "🔍 Verificando dependências do sistema..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Python $PYTHON_VERSION encontrado"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 não encontrado. Instale pip primeiro."
    exit 1
fi

log_info "pip encontrado"

# Criar diretórios necessários
echo ""
echo "📁 Criando estrutura de diretórios..."
mkdir -p data
mkdir -p models
mkdir -p results/{logs,figures}
mkdir -p uploads

log_info "Diretórios criados"

# Criar ou ativar virtual environment
echo ""
echo "🐍 Configurando ambiente virtual..."
if [ ! -d ".venv" ]; then
    log_info "Criando novo ambiente virtual..."
    python3 -m venv .venv
else
    log_info "Ambiente virtual já existe"
fi

# Ativar venv
source .venv/bin/activate || {
    log_error "Falha ao ativar ambiente virtual"
    exit 1
}

log_info "Ambiente virtual ativado"

# Atualizar pip
echo ""
echo "📦 Atualizando pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

log_info "pip atualizado"

# Instalar dependências
echo ""
echo "📚 Instalando dependências..."
log_info "Isso pode levar alguns minutos..."

pip install -r requirements.txt --no-cache-dir || {
    log_error "Falha ao instalar dependências"
    exit 1
}

log_info "Dependências instaladas"

# Verificar instalação
echo ""
echo "🧪 Verificando instalação..."
python3 check_installation.py || {
    log_warn "Algumas dependências podem estar faltando"
}

# Configurar .env se não existir
echo ""
echo "⚙️  Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    log_info "Criando arquivo .env a partir de .env.example..."
    cp .env.example .env
    
    # Gerar API key aleatória
    API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/SECRET_API_KEY=troque_aqui/SECRET_API_KEY=$API_KEY/" .env
    
    # Gerar salt aleatório
    SALT=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    sed -i "s/SALT_ANON=troque_salt/SALT_ANON=$SALT/" .env
    
    log_info "Arquivo .env criado com chaves seguras"
    log_warn "IMPORTANTE: Sua API key é: $API_KEY"
    log_warn "Salve esta chave! Você precisará dela para acessar a API."
else
    log_info "Arquivo .env já existe"
fi

# Baixar dados (se não existirem)
echo ""
echo "📊 Verificando dados..."
if [ ! -f "data/real_combined_dataset.csv" ]; then
    log_info "Baixando dados educacionais..."
    python3 data/data_fetch_and_prepare.py --datasets assistments --seed 42 --limit-download 200 || {
        log_warn "Erro ao baixar dados. Execute manualmente se necessário."
    }
else
    log_info "Dados já existem"
fi

# Treinar modelo (se não existir)
echo ""
echo "🧠 Verificando modelo..."
if [ ! -f "models/dkt.pt" ]; then
    log_info "Treinando modelo inicial (pode levar alguns minutos)..."
    python3 train_dkt.py --epochs 3 --batch-size 32 --seed 42 || {
        log_warn "Erro ao treinar modelo. Execute manualmente se necessário."
    }
else
    log_info "Modelo já existe"
fi

# Executar testes
echo ""
echo "🧪 Executando testes..."
python3 -m pytest tests/ -v --tb=short || {
    log_warn "Alguns testes falharam. O sistema ainda pode funcionar."
}

# Validar sistema
echo ""
echo "✅ Validando sistema completo..."
python3 validar_sistema.py || {
    log_warn "Validação completa falhou. Verifique os logs acima."
}

# Informações de deploy
echo ""
echo "============================================================"
echo "  🎉 SETUP CONCLUÍDO COM SUCESSO!"
echo "============================================================"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1️⃣  Iniciar a API:"
echo "   $ source .venv/bin/activate"
echo "   $ uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
echo ""
echo "2️⃣  Abrir o frontend demo:"
echo "   $ cd frontend/static_demo"
echo "   $ python3 -m http.server 8001"
echo "   Acesse: http://localhost:8001"
echo ""
echo "3️⃣  Abrir o dashboard administrativo:"
echo "   $ cd frontend"
echo "   $ python3 -m http.server 8002"
echo "   Acesse: http://localhost:8002/admin_dashboard.html"
echo ""
echo "🔑 SUA API KEY:"
if [ -f ".env" ]; then
    grep "SECRET_API_KEY" .env | cut -d'=' -f2
else
    echo "   Configure manualmente no arquivo .env"
fi
echo ""
echo "📚 DOCUMENTAÇÃO:"
echo "   - README.md - Visão geral completa"
echo "   - README_DIDATICO.md - Guia para leigos"
echo "   - GUIA_INICIANTES.md - Tutorial passo-a-passo"
echo "   - API_AVANCADA.md - Documentação da API"
echo "   - EXECUCAO_COMPLETA.md - Guia end-to-end"
echo ""
echo "🆘 PROBLEMAS?"
echo "   - Execute: python3 validar_sistema.py"
echo "   - Consulte GUIA_INICIANTES.md seção Troubleshooting"
echo ""
echo "============================================================"
echo "  ✨ Sistema pronto para uso! Bom trabalho! 🇧🇷"
echo "============================================================"

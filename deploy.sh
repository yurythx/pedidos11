#!/bin/bash

################################################################################
# DEPLOY AUTOMATIZADO - Projeto Nix
# Versão: 1.0.0
# Descrição: Script completo para deploy em Ubuntu com validações
################################################################################

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Auto-detectar diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/deploy.log"
MAX_BACKUPS=5
HEALTH_CHECK_TIMEOUT=60
REQUIRED_DISK_SPACE=1000000  # 1GB em KB

# Criar diretórios necessários
mkdir -p "$BACKUP_DIR"
touch "$LOG_FILE"

################################################################################
# FUNÇÕES AUXILIARES
################################################################################

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

################################################################################
# CRIAR ARQUIVOS .ENV SE NÃO EXISTIREM
################################################################################

create_env_files() {
    log "🔧 Verificando arquivos .env..."
    
    # Backend .env
    if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
        warning "Arquivo backend/.env não encontrado. Criando..."
        
        # Gerar SECRET_KEY aleatória
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || \
                     openssl rand -base64 50 2>/dev/null || \
                     cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)
        
        # Solicitar informações
        read -p "Digite o domínio do servidor (ex: api.seudominio.com): " DOMAIN
        DOMAIN=${DOMAIN:-localhost}
        
        read -p "Digite a senha do banco PostgreSQL [nix_password_2026]: " DB_PASSWORD
        DB_PASSWORD=${DB_PASSWORD:-nix_password_2026}
        
        # Criar arquivo .env
        cat > "$PROJECT_DIR/backend/.env" << EOF
# Django Settings
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://nix_user:$DB_PASSWORD@db:5432/nix_db

# CORS
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,http://localhost:3002,http://$DOMAIN:3002

# Security
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Email (opcional - configure depois)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=seu-email@gmail.com
# EMAIL_HOST_PASSWORD=sua-senha-app

# Sentry (opcional)
# SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
EOF
        
        success "Arquivo backend/.env criado!"
        log "SECRET_KEY gerada automaticamente"
        log "Domínio configurado: $DOMAIN"
    else
        success "Arquivo backend/.env já existe"
    fi
    
    # Frontend .env.local
    if [ ! -f "$PROJECT_DIR/frontend/.env.local" ]; then
        warning "Arquivo frontend/.env.local não encontrado. Criando..."
        
        # Usar mesmo domínio do backend
if [ -z "$DOMAIN" ]; then
            read -p "Digite o domínio do servidor (ex: seudominio.com): " DOMAIN
            DOMAIN=${DOMAIN:-localhost}
        fi
        
        cat > "$PROJECT_DIR/frontend/.env.local" << EOF
# API URL
NEXT_PUBLIC_API_URL=http://$DOMAIN:8002/api/v1

# App Info
NEXT_PUBLIC_APP_NAME=Projeto Nix
NEXT_PUBLIC_APP_VERSION=1.0.0

# Environment
NEXT_PUBLIC_ENV=production
EOF
        
        success "Arquivo frontend/.env.local criado!"
    else
        success "Arquivo frontend/.env.local já existe"
    fi
    
    # Atualizar docker-compose.prod.yml com senha do banco
    if [ ! -z "$DB_PASSWORD" ] && [ -f "$PROJECT_DIR/docker-compose.prod.yml" ]; then
        log "Atualizando senha do banco no docker-compose.prod.yml..."
        sed -i "s/POSTGRES_PASSWORD:.*/POSTGRES_PASSWORD: $DB_PASSWORD/" "$PROJECT_DIR/docker-compose.prod.yml"
    fi
}

################################################################################
# VERIFICAÇÕES PRÉ-DEPLOY
################################################################################

check_prerequisites() {
    log "🔍 Verificando pré-requisitos..."
    
    # Docker instalado?
    if ! command -v docker &> /dev/null; then
        error "Docker não instalado!"
        exit 1
    fi
    success "Docker instalado"
    
    # Docker Compose instalado?
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não instalado!"
        exit 1
    fi
    success "Docker Compose instalado"
    
    # Git instalado?
    if ! command -v git &> /dev/null; then
        error "Git não instalado!"
        exit 1
    fi
    success "Git instalado"
    
    # Espaço em disco suficiente?
    available_space=$(df "$PROJECT_DIR" | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt "$REQUIRED_DISK_SPACE" ]; then
        error "Espaço em disco insuficiente! Necessário: ${REQUIRED_DISK_SPACE}KB, Disponível: ${available_space}KB"
        exit 1
    fi
    success "Espaço em disco suficiente: $(( available_space / 1024 ))MB disponíveis"
    
    # Diretório do projeto existe?
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Diretório do projeto não existe: $PROJECT_DIR"
        exit 1
    fi
    success "Diretório do projeto OK"
    
    # Arquivo .env existe?
    if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
        error "Arquivo backend/.env não encontrado!"
        exit 1
    fi
    success "Arquivo .env do backend OK"
    
    if [ ! -f "$PROJECT_DIR/frontend/.env.local" ]; then
        warning "Arquivo frontend/.env.local não encontrado (não crítico)"
    else
        success "Arquivo .env do frontend OK"
    fi
}

################################################################################
# BACKUP
################################################################################

create_backup() {
    log "💾 Criando backup..."
    
    # Criar diretório de backup
    mkdir -p "$BACKUP_DIR"
    
    # Nome do backup com timestamp
    BACKUP_NAME="backup_$(date +'%Y%m%d_%H%M%S')"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    # Backup do banco de dados
    log "Backup do banco de dados..."
    docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T db \
        pg_dump -U nix_user nix_db > "$BACKUP_PATH.sql" 2>/dev/null || {
        warning "Não foi possível fazer backup do banco (pode não existir ainda)"
    }
    
    # Backup dos arquivos de configuração
    log "Backup dos arquivos de configuração..."
    tar -czf "$BACKUP_PATH.tar.gz" \
        -C "$PROJECT_DIR" \
        backend/.env \
        frontend/.env.local \
        docker-compose.prod.yml \
        2>/dev/null || true
    
    success "Backup criado: $BACKUP_NAME"
    
    # Limpar backups antigos (manter apenas os últimos MAX_BACKUPS)
    log "Limpando backups antigos..."
    cd "$BACKUP_DIR"
    ls -t backup_*.sql 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
    ls -t backup_*.tar.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
    success "Backups antigos limpos"
}

################################################################################
# GIT PULL
################################################################################

update_code() {
    log "📥 Atualizando código..."
    
    cd "$PROJECT_DIR"
    
    # Verificar se há mudanças locais
    if ! git diff-index --quiet HEAD --; then
        warning "Existem mudanças locais não commitadas!"
        read -p "Descartar mudanças locais? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            git reset --hard HEAD
        else
            error "Deploy cancelado pelo usuário"
            exit 1
        fi
    fi
    
    # Pull do código
    CURRENT_COMMIT=$(git rev-parse HEAD)
    git pull origin main || {
        error "Erro ao fazer pull do código!"
        exit 1
    }
    NEW_COMMIT=$(git rev-parse HEAD)
    
    if [ "$CURRENT_COMMIT" != "$NEW_COMMIT" ]; then
        success "Código atualizado: $CURRENT_COMMIT -> $NEW_COMMIT"
        echo "$NEW_COMMIT" > /tmp/new_commit
    else
        log "Código já está atualizado"
        echo "$CURRENT_COMMIT" > /tmp/new_commit
    fi
}

################################################################################
# VALIDAÇÕES
################################################################################

validate_config() {
    log "🔍 Validando configurações..."
    
    # Verificar variáveis críticas no backend/.env
    if ! grep -q "SECRET_KEY=" "$PROJECT_DIR/backend/.env"; then
        error "SECRET_KEY não configurada no backend/.env!"
        exit 1
    fi
    
    if ! grep -q "DATABASE_URL=" "$PROJECT_DIR/backend/.env"; then
        error "DATABASE_URL não configurada no backend/.env!"
        exit 1
    fi
    
    # Verificar se DEBUG está False em produção
    if grep -q "DEBUG=True" "$PROJECT_DIR/backend/.env"; then
        warning "DEBUG=True detectado! Recomendado DEBUG=False em produção"
        read -p "Continuar mesmo assim? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    fi
    
    success "Configurações validadas"
}

################################################################################
# BUILD
################################################################################

build_containers() {
    log "🔨 Buildando containers..."
    
    cd "$PROJECT_DIR"
    
    # Build com no-cache para garantir versão mais recente
    docker-compose -f docker-compose.prod.yml build --no-cache || {
        error "Erro ao buildar containers!"
        exit 1
    }
    
    success "Build concluído"
}

################################################################################
# DEPLOY
################################################################################

deploy_containers() {
    log "🚀 Fazendo deploy..."
    
    cd "$PROJECT_DIR"
    
    # Parar containers atuais
    log "Parando containers atuais..."
    docker-compose -f docker-compose.prod.yml down || {
        warning "Erro ao parar containers (pode não estar rodando)"
    }
    
    # Subir novos containers
    log "Subindo novos containers..."
    docker-compose -f docker-compose.prod.yml up -d || {
        error "Erro ao subir containers!"
        return 1
    }
    
    success "Containers iniciados"
    return 0
}

################################################################################
# MIGRATIONS
################################################################################

run_migrations() {
    log "🗄️  Executando migrations..."
    
    # Aguardar backend estar pronto
    log "Aguardando backend ficar pronto..."
    sleep 10
    
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.prod.yml exec -T backend \
        python manage.py migrate --noinput || {
        error "Erro ao executar migrations!"
        return 1
    }
    
    success "Migrations executadas"
    
    # Coletar arquivos estáticos
    log "Coletando arquivos estáticos..."
    docker-compose -f docker-compose.prod.yml exec -T backend \
        python manage.py collectstatic --noinput || {
        warning "Erro ao coletar static files (não crítico)"
    }
    
    return 0
}

################################################################################
# HEALTH CHECKS
################################################################################

health_check() {
    log "🏥 Verificando saúde dos serviços..."
    
    local timeout=$HEALTH_CHECK_TIMEOUT
    local elapsed=0
    
    # Backend health check
    log "Verificando backend..."
    while [ $elapsed -lt $timeout ]; do
        if curl -sf http://localhost:8002/admin/ > /dev/null 2>&1; then
            success "Backend está saudável"
            break
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done
    
    if [ $elapsed -ge $timeout ]; then
        error "Backend health check falhou (timeout: ${timeout}s)"
        return 1
    fi
    
    # Frontend health check
    log "Verificando frontend..."
    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -sf http://localhost:3002 > /dev/null 2>&1; then
            success "Frontend está saudável"
            break
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done
    
    if [ $elapsed -ge $timeout ]; then
        error "Frontend health check falhou (timeout: ${timeout}s)"
        return 1
    fi
    
    # Database health check
    log "Verificando banco de dados..."
    if docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T db \
        pg_isready -U nix_user > /dev/null 2>&1; then
        success "Banco de dados está saudável"
    else
        error "Banco de dados health check falhou"
        return 1
    fi
    
    success "Todos os serviços estão saudáveis"
    return 0
}

################################################################################
# ROLLBACK
################################################################################

rollback() {
    error "🔙 Iniciando rollback..."
    
    # Parar containers com problema
    docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" down
    
    # Restaurar código anterior
    if [ -f /tmp/previous_commit ]; then
        PREVIOUS_COMMIT=$(cat /tmp/previous_commit)
        cd "$PROJECT_DIR"
        git reset --hard "$PREVIOUS_COMMIT"
        success "Código revertido para: $PREVIOUS_COMMIT"
    fi
    
    # Rebuild com versão anterior
    log "Rebuilding com código anterior..."
    docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" build
    
    # Subir containers
    docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" up -d
    
    # Aguardar e verificar
    sleep 10
    if health_check; then
        success "Rollback concluído com sucesso"
    else
        error "Rollback falhou! Intervenção manual necessária"
        exit 1
    fi
}

################################################################################
# MAIN
################################################################################

main() {
    log "═══════════════════════════════════════════════════════════"
    log "🚀 INICIANDO DEPLOY AUTOMATIZADO - Projeto Nix"
    log "═══════════════════════════════════════════════════════════"
    
    # Salvar commit atual para possível rollback
    if [ -d "$PROJECT_DIR/.git" ]; then
        cd "$PROJECT_DIR"
        git rev-parse HEAD > /tmp/previous_commit
    fi
    
    # 0. Criar arquivos .env se necessário
    create_env_files
    
    # 1. Verificações pré-deploy
    check_prerequisites
    
    # 2. Backup
    create_backup
    
    # 3. Atualizar código
    update_code
    
    # 4. Validar configurações
    validate_config
    
    # 5. Build
    build_containers
    
    # 6. Deploy
    if ! deploy_containers; then
        error "Deploy falhou!"
        rollback
        exit 1
    fi
    
    # 7. Migrations
    if ! run_migrations; then
        error "Migrations falharam!"
        rollback
        exit 1
    fi
    
    # 8. Health checks
    if ! health_check; then
        error "Health checks falharam!"
        rollback
        exit 1
    fi
    
    # 9. Limpeza
    log "🧹 Limpando imagens antigas..."
    docker image prune -f > /dev/null 2>&1 || true
    
    # 10. Sucesso!
    log "═══════════════════════════════════════════════════════════"
    success "✨ DEPLOY CONCLUÍDO COM SUCESSO!"
    log "═══════════════════════════════════════════════════════════"
    log ""
    log "📊 Informações do Deploy:"
    log "   - Commit: $(cat /tmp/new_commit)"
    log "   - Data: $(date +'%Y-%m-%d %H:%M:%S')"
    log "   - Backend: http://localhost:8002"
    log "   - Frontend: http://localhost:3002"
    log ""
    log "📝 Logs salvos em: $LOG_FILE"
    log "💾 Backup salvo em: $BACKUP_DIR"
}

# Executar main
main "$@"

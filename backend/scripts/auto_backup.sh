#!/bin/bash

################################################################################
# SCRIPT DE BACKUP AUTOMATIZADO - Projeto Nix
################################################################################

# Configurações
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
BACKUP_DIR="$PROJECT_DIR/backups/db"
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
BACKUP_FILE="$BACKUP_DIR/nix_db_$TIMESTAMP.sql"
MAX_BACKUPS=30 # Manter um mês de backups

# Criar diretório se não existir
mkdir -p "$BACKUP_DIR"

echo "🔄 Iniciando backup do banco de dados..."

# Executar o dump via Docker
docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T db \
    pg_dump -U nix_user nix_db > "$BACKUP_FILE"

# Comprimir para economizar espaço
gzip "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup concluído com sucesso: ${BACKUP_FILE}.gz"
    
    # Limpar backups mais antigos que X dias
    find "$BACKUP_DIR" -name "nix_db_*.sql.gz" -mtime +$MAX_BACKUPS -delete
    echo "🧹 Backups antigos removidos (mantendo últimos $MAX_BACKUPS)."
else
    echo "❌ FALHA NO BACKUP!"
    exit 1
fi

# DEPLOY AUTOMATIZADO - Projeto Nix (PowerShell version)
# Versão: 1.0.0
# Descrição: Script completo para deploy local com validações

param(
    [switch]$SkipBackup,
    [switch]$SkipHealthCheck,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Configurações
$PROJECT_DIR = $PSScriptRoot
$BACKUP_DIR = Join-Path $PROJECT_DIR "backups"
$LOG_FILE = Join-Path $PROJECT_DIR "deploy.log"
$MAX_BACKUPS = 5

################################################################################
# FUNÇÕES AUXILIARES
################################################################################

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "Cyan" }
    }
    
    $prefix = switch ($Level) {
        "SUCCESS" { "✅" }
        "ERROR" { "❌" }
        "WARNING" { "⚠️ " }
        default { "ℹ️ " }
    }
    
    $logMessage = "[$timestamp] $prefix $Message"
    Write-Host $logMessage -ForegroundColor $color
    Add-Content -Path $LOG_FILE -Value $logMessage
}

################################################################################
# VERIFICAÇÕES PRÉ-DEPLOY
################################################################################

function Test-Prerequisites {
    Write-Log "🔍 Verificando pré-requisitos..." "INFO"
    
    # Docker instalado?
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Log "Docker não instalado!" "ERROR"
        exit 1
    }
    Write-Log "Docker instalado" "SUCCESS"
    
    # Docker está rodando?
    try {
        docker ps | Out-Null
    } catch {
        Write-Log "Docker não está rodando!" "ERROR"
        exit 1
    }
    Write-Log "Docker está rodando" "SUCCESS"
    
    # Docker Compose instalado?
    if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Log "Docker Compose não instalado!" "ERROR"
        exit 1
    }
    Write-Log "Docker Compose instalado" "SUCCESS"
    
    # Espaço em disco
    $drive = (Get-Item $PROJECT_DIR).PSDrive
    $freeSpace = (Get-PSDrive $drive.Name).Free / 1MB
    if ($freeSpace -lt 1000) {
        Write-Log "Espaço em disco insuficiente! Disponível: $([math]::Round($freeSpace))MB" "ERROR"
        exit 1
    }
    Write-Log "Espaço em disco OK: $([math]::Round($freeSpace))MB disponíveis" "SUCCESS"
    
    # Arquivos .env existem?
    $backendEnv = Join-Path $PROJECT_DIR "backend\.env"
    if (!(Test-Path $backendEnv)) {
        Write-Log "Arquivo backend\.env não encontrado!" "ERROR"
        exit 1
    }
    Write-Log "Arquivo .env do backend OK" "SUCCESS"
    
    $frontendEnv = Join-Path $PROJECT_DIR "frontend\.env.local"
    if (!(Test-Path $frontendEnv)) {
        Write-Log "Arquivo frontend\.env.local não encontrado (não crítico)" "WARNING"
    } else {
        Write-Log "Arquivo .env do frontend OK" "SUCCESS"
    }
}

################################################################################
# BACKUP
################################################################################

function New-Backup {
    if ($SkipBackup) {
        Write-Log "Backup pulado (--SkipBackup)" "WARNING"
        return
    }
    
    Write-Log "💾 Criando backup..." "INFO"
    
    # Criar diretório de backup
    if (!(Test-Path $BACKUP_DIR)) {
        New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
    }
    
    $backupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    $backupPath = Join-Path $BACKUP_DIR $backupName
    
    # Backup do banco (se estiver rodando)
    try {
        Write-Log "Backup do banco de dados..." "INFO"
        docker-compose -f docker-compose.yml exec -T db pg_dump -U nix_user nix_db > "$backupPath.sql"
        Write-Log "Backup do banco concluído" "SUCCESS"
    } catch {
        Write-Log "Não foi possível fazer backup do banco (pode não estar rodando)" "WARNING"
    }
    
    # Backup dos arquivos de configuração
    Write-Log "Backup dos arquivos de configuração..." "INFO"
    $filesToBackup = @(
        "backend\.env",
        "frontend\.env.local",
        "docker-compose.yml",
        "docker-compose.prod.yml"
    )
    
    $tempBackupDir = New-Item -ItemType Directory -Path (Join-Path $BACKUP_DIR "temp_$backupName")
    foreach ($file in $filesToBackup) {
        $sourcePath = Join-Path $PROJECT_DIR $file
        if (Test-Path $sourcePath) {
            $destPath = Join-Path $tempBackupDir (Split-Path $file -Leaf)
            Copy-Item $sourcePath $destPath
        }
    }
    
    Compress-Archive -Path "$tempBackupDir\*" -DestinationPath "$backupPath.zip"
    Remove-Item $tempBackupDir -Recurse -Force
    
    Write-Log "Backup criado: $backupName" "SUCCESS"
    
    # Limpar backups antigos
    Write-Log "Limpando backups antigos..." "INFO"
    Get-ChildItem $BACKUP_DIR -Filter "backup_*.sql" | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -Skip $MAX_BACKUPS | 
        Remove-Item -Force
    Get-ChildItem $BACKUP_DIR -Filter "backup_*.zip" | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -Skip $MAX_BACKUPS | 
        Remove-Item -Force
}

################################################################################
# VALIDAÇÕES
################################################################################

function Test-Configuration {
    Write-Log "🔍 Validando configurações..." "INFO"
    
    $backendEnv = Join-Path $PROJECT_DIR "backend\.env"
    $envContent = Get-Content $backendEnv -Raw
    
    # Verificar SECRET_KEY
    if ($envContent -notmatch "SECRET_KEY=") {
        Write-Log "SECRET_KEY não configurada!" "ERROR"
        exit 1
    }
    
    # Verificar DATABASE_URL
    if ($envContent -notmatch "DATABASE_URL=") {
        Write-Log "DATABASE_URL não configurada!" "ERROR"
        exit 1
    }
    
    # Avisar se DEBUG=True
    if ($envContent -match "DEBUG=True") {
        Write-Log "DEBUG=True detectado! Recomendado DEBUG=False em produção" "WARNING"
        if (!$Force) {
            $response = Read-Host "Continuar mesmo assim? (s/N)"
            if ($response -ne "s" -and $response -ne "S") {
                exit 1
            }
        }
    }
    
    Write-Log "Configurações validadas" "SUCCESS"
}

################################################################################
# BUILD E DEPLOY
################################################################################

function Start-Build {
    Write-Log "🔨 Buildando containers..." "INFO"
    
    Push-Location $PROJECT_DIR
    try {
        docker-compose build --no-cache
        Write-Log "Build concluído" "SUCCESS"
    } catch {
        Write-Log "Erro ao buildar containers!" "ERROR"
        throw
    } finally {
        Pop-Location
    }
}

function Start-Deploy {
    Write-Log "🚀 Fazendo deploy..." "INFO"
    
    Push-Location $PROJECT_DIR
    try {
        # Parar containers
        Write-Log "Parando containers atuais..." "INFO"
        docker-compose down 2>&1 | Out-Null
        
        # Subir novos containers
        Write-Log "Subindo novos containers..." "INFO"
        docker-compose up -d
        
        Write-Log "Containers iniciados" "SUCCESS"
    } catch {
        Write-Log "Erro ao fazer deploy!" "ERROR"
        throw
    } finally {
        Pop-Location
    }
}

################################################################################
# HEALTH CHECKS
################################################################################

function Test-Health {
    if ($SkipHealthCheck) {
        Write-Log "Health check pulado (--SkipHealthCheck)" "WARNING"
        return $true
    }
    
    Write-Log "🏥 Verificando saúde dos serviços..." "INFO"
    
    $timeout = 60
    $elapsed = 0
    
    # Backend
    Write-Log "Verificando backend..." "INFO"
    while ($elapsed -lt $timeout) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/admin/" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                Write-Log "Backend está saudável" "SUCCESS"
                break
            }
        } catch {
            Start-Sleep -Seconds 2
            $elapsed += 2
        }
    }
    
    if ($elapsed -ge $timeout) {
        Write-Log "Backend health check falhou (timeout: ${timeout}s)" "ERROR"
        return $false
    }
    
    # Frontend
    Write-Log "Verificando frontend..." "INFO"
    $elapsed = 0
    while ($elapsed -lt $timeout) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                Write-Log "Frontend está saudável" "SUCCESS"
                break
            }
        } catch {
            Start-Sleep -Seconds 2
            $elapsed += 2
        }
    }
    
    if ($elapsed -ge $timeout) {
        Write-Log "Frontend health check falhou (timeout: ${timeout}s)" "ERROR"
        return $false
    }
    
    Write-Log "Todos os serviços estão saudáveis" "SUCCESS"
    return $true
}

################################################################################
# MAIN
################################################################################

function Main {
    Write-Log "═══════════════════════════════════════════════════════════" "INFO"
    Write-Log "🚀 INICIANDO DEPLOY AUTOMATIZADO - Projeto Nix" "INFO"
    Write-Log "═══════════════════════════════════════════════════════════" "INFO"
    
    try {
        # 1. Verificações pré-deploy
        Test-Prerequisites
        
        # 2. Backup
        New-Backup
        
        # 3. Validar configurações
        Test-Configuration
        
        # 4. Build
        Start-Build
        
        # 5. Deploy
        Start-Deploy
        
        # 6. Aguardar serviços
        Write-Log "⏳ Aguardando serviços iniciarem..." "INFO"
        Start-Sleep -Seconds 10
        
        # 7. Health checks
        if (!(Test-Health)) {
            Write-Log "Health checks falharam!" "ERROR"
            throw "Deploy falhou nos health checks"
        }
        
        # 8. Limpeza
        Write-Log "🧹 Limpando recursos..." "INFO"
        docker image prune -f | Out-Null
        
        # 9. Sucesso!
        Write-Log "═══════════════════════════════════════════════════════════" "INFO"
        Write-Log "✨ DEPLOY CONCLUÍDO COM SUCESSO!" "SUCCESS"
        Write-Log "═══════════════════════════════════════════════════════════" "INFO"
        Write-Log "" "INFO"
        Write-Log "📊 Informações do Deploy:" "INFO"
        Write-Log "   - Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"
        Write-Log "   - Backend: http://localhost:8000" "INFO"  
        Write-Log "   - Frontend: http://localhost:3000" "INFO"
        Write-Log "" "INFO"
        Write-Log "📝 Logs salvos em: $LOG_FILE" "INFO"
        Write-Log "💾 Backup salvo em: $BACKUP_DIR" "INFO"
        
    } catch {
        Write-Log "❌ DEPLOY FALHOU: $_" "ERROR"
        Write-Log "Verifique os logs em: $LOG_FILE" "ERROR"
        exit 1
    }
}

# Executar
Main

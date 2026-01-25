# 🚀 Deploy Automatizado - Guia de Uso

**Scripts prontos para deploy com 1 comando**

---

## 📁 Arquivos Criados

### Para Linux/Ubuntu (Servidor)
- **`deploy.sh`** - Script bash completo

### Para Windows (Desenvolvimento local)
- **`deploy.ps1`** - Script PowerShell completo

---

## 🎯 CARACTERÍSTICAS

### ✅ Verificações Automáticas
- Docker instalado e rodando
- Docker Compose disponível
- Espaço em disco suficiente
- Arquivos .env configurados
- Variáveis críticas presentes

### 💾 Backup Automático
- Banco de dados (PostgreSQL)
- Arquivos de configuração (.env)
- Mantém últimos 5 backups
-Limpeza automática de backups antigos

### 🔍 Validações
- SECRET_KEY configurada
- DATABASE_URL configurada
- DEBUG=False em produção
- Configurações críticas presentes

### 🏥 Health Checks
- Backend (Django/API)
- Frontend (Next.js)
- Banco de dados
- Timeout configurável (60s padrão)

### 🔄 Rollback Automático
- Se build falhar → rollback
- Se deploy falhar → rollback
- Se health check falhar → rollback
- Restaura código anterior
- Restaura containers anteriores

### 📊 Logs Detalhados
- Coloridos no terminal
- Salvos em arquivo
- Timestamps
- Níveis (INFO, SUCCESS, ERROR, WARNING)

---

## 🚀 USO - LINUX/UBUNTU (Servidor)

### Setup Inicial (uma vez)

```bash
# 1. Copiar script para servidor
scp deploy.sh user@servidor:/home/deploy/pedidos11/

# 2. No servidor - dar permissão
cd /home/deploy/pedidos11
chmod +x deploy.sh

# 3. Editar configurações no script (se necessário)
nano deploy.sh
# Ajustar PROJECT_DIR, BACKUP_DIR, etc
```

### Executar Deploy

```bash
# Deploy completo
./deploy.sh

# Ver logs em tempo real
tail -f /home/deploy/deploy.log
```

### Opções Avançadas

```bash
# Ver log anterior
cat /home/deploy/deploy.log

# Ver backups
ls -lh /home/deploy/backups/

# Restaurar backup manual
cat /home/deploy/backups/backup_YYYYMMDD_HHMMSS.sql | \
  docker-compose -f docker-compose.prod.yml exec -T db psql -U nix_user -d nix_db
```

---

## 🪟 USO - WINDOWS (Desenvolvimento Local)

### Executar Deploy

```powershell
# PowerShell como Administrador
cd "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11"

# Deploy completo
.\deploy.ps1

# Deploy sem backup
.\deploy.ps1 -SkipBackup

# Deploy sem health check
.\deploy.ps1 -SkipHealthCheck

# Deploy forçado (não pede confirmação)
.\deploy.ps1 -Force

# Combinado
.\deploy.ps1 -SkipBackup -Force
```

### Ver Logs

```powershell
# Ver log
Get-Content deploy.log -Tail 50

# Acompanhar em tempo real
Get-Content deploy.log -Wait
```

---

## 🔧 CONFIGURAÇÃO

### Editar Configurações (Linux)

```bash
nano deploy.sh
```

**Configurações disponíveis:**

```bash
PROJECT_DIR="/home/deploy/pedidos11"    # Diretório do projeto
BACKUP_DIR="/home/deploy/backups"       # Onde salvar backups
LOG_FILE="/home/deploy/deploy.log"      # Arquivo de log
MAX_BACKUPS=5                            # Número de backups a manter
HEALTH_CHECK_TIMEOUT=60                  # Timeout em segundos
REQUIRED_DISK_SPACE=1000000              # Espaço mínimo (KB)
```

### Editar Configurações (Windows)

```powershell
notepad deploy.ps1
```

**Configurações disponíveis:**

```powershell
$PROJECT_DIR = $PSScriptRoot                # Auto-detecta
$BACKUP_DIR = Join-Path $PROJECT_DIR "backups"
$LOG_FILE = Join-Path $PROJECT_DIR "deploy.log"
$MAX_BACKUPS = 5
```

---

## 📊 FLUXO DO DEPLOY

```
1. ✅ Verificações Pré-Deploy
   ├─ Docker instalado?
   ├─ Docker Compose instalado?
   ├─ Espaço em disco OK?
   ├─ Diretório existe?
   └─ Arquivos .env existem?

2. 💾 Backup
   ├─ Criar diretório de backup
   ├─ Backup do banco PostgreSQL
   ├─ Backup dos .env
   └─ Limpar backups antigos

3. 📥 Atualizar Código (Linux)
   ├─ Git pull origin main
   ├─ Verificar mudanças
   └─ Salvar commit para rollback

4. 🔍 Validar Configurações
   ├─ SECRET_KEY presente?
   ├─ DATABASE_URL presente?
   └─ DEBUG=False? (aviso)

5. 🔨 Build
   └─ docker-compose build --no-cache

6. 🚀 Deploy
   ├─ docker-compose down
   └─ docker-compose up -d

7. 🗄️  Migrations (Linux)
   ├─ migrate --noinput
   └─ collectstatic --noinput

8. 🏥 Health Checks
   ├─ Backend (http://localhost:8000)
   ├─ Frontend (http://localhost:3000)
   └─ Database (pg_isready)

9. ✅ Sucesso!
   └─ Limpar imagens antigas

❌ Se falhar em qualquer etapa:
   └─ Rollback automático
```

---

## 🐛 TROUBLESHOOTING

### "Docker não instalado"
```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### "Permissão negada"
```bash
# Dar permissão
chmod +x deploy.sh

# Ou executar com sudo
sudo ./deploy.sh
```

### "Espaço em disco insuficiente"
```bash
# Limpar Docker
docker system prune -a

# Ver espaço
df -h
```

### "Health check falhou"
```bash
# Ver logs dos containers
docker-compose logs backend
docker-compose logs frontend

# Ver status
docker-compose ps
```

### "Rollback falhou"
```bash
# Parar tudo
docker-compose down

# Restaurar backup manual
cat /path/to/backup.sql | docker-compose exec -T db psql -U nix_user -d nix_db

# Rebuild
docker-compose build
docker-compose up -d
```

---

## 🎯 EXEMPLOS DE USO

### Desenvolvimento Local (Windows)

```powershell
# Deploy rápido sem backup
.\deploy.ps1 -SkipBackup -SkipHealthCheck

# Deploy normal
.\deploy.ps1
```

### Produção (Linux)

```bash
# Deploy normal
./deploy.sh

# Agendar deploy automático (cron)
# Editar crontab
crontab -e

# Adicionar linha (deploy todo dia às 3h)
0 3 * * * /home/deploy/pedidos11/deploy.sh >> /home/deploy/deploy-cron.log 2>&1
```

---

## 📝 LOGS

### Formato do Log

```
[2026-01-25 17:00:00] ℹ️  🔍 Verificando pré-requisitos...
[2026-01-25 17:00:01] ✅ Docker instalado
[2026-01-25 17:00:02] ✅ Docker Compose instalado
[2026-01-25 17:00:03] ℹ️  💾 Criando backup...
[2026-01-25 17:00:10] ✅ Backup criado: backup_20260125_170000
...
[2026-01-25 17:05:00] ✅ ✨ DEPLOY CONCLUÍDO COM SUCESSO!
```

### Ver Logs

```bash
# Linux
tail -f /home/deploy/deploy.log

# Windows
Get-Content deploy.log -Wait
```

---

## ✅ CHECKLIST DE USO

### Primeira Vez (Setup)

- [ ] Script copiado para servidor/projeto
- [ ] Permissões configuradas (chmod +x)
- [ ] Configurações ajustadas (PROJECT_DIR, etc)
- [ ] Docker instalado e rodando
- [ ] .env files configurados
- [ ] Testado uma vez

### Cada Deploy

- [ ] Código commitado e pushed
- [ ] Mudanças revisadas
- [ ] Executar script
- [ ] Verificar logs
- [ ] Testar aplicação
- [ ] Validar em produção

---

## 🔒 SEGURANÇA

### Boas Práticas

- ✅ Sempre fazer backup antes
- ✅ Revisar mudanças antes do deploy
- ✅ Testar em staging primeiro
- ✅ Ter plano de rollback
- ✅ Monitorar logs após deploy
- ✅ Validar health checks
- ✅ Não commitar .env
- ✅ Usar secrets do GitHub

### Em Produção

- ✅ DEBUG=False sempre
- ✅ SECRET_KEY forte e única
- ✅ DATABASE_URL seguro
- ✅ HTTPS configurado
- ✅ Firewall ativo
- ✅ Backups automáticos
- ✅ Monitoring ativo

---

## 🚀 INTEGRAÇÃO CI/CD

### Com GitHub Actions

O deploy manual complementa o CI/CD automático:

- **GitHub Actions:** Deploy automático em push
- **Script manual:** Deploy sob demanda ou emergencial

```yaml
# .github/workflows/ci-cd.yml já configurado
# Para deploy manual, use os scripts
```

---

## 📞 SUPORTE

**Problemas?**
1. Ver logs: `cat deploy.log`
2. Ver status: `docker-compose ps`
3. Ver logs containers: `docker-compose logs`
4. Verificar documentação: `docs/DEPLOY_UBUNTU.md`

---

## 🎉 BENEFÍCIOS

✅ **1 comando** para deploy completo  
✅ **Verificações automáticas** (11 checks)  
✅ **Backup automático** antes do deploy  
✅ **Health checks** após deploy  
✅ **Rollback automático** se falhar  
✅ **Logs detalhados** coloridos  
✅ **Seguro** e **confiável**  
✅ **Fácil** de usar  

---

**Deploy automatizado pronto!** 🚀

**Última atualização:** 25/01/2026

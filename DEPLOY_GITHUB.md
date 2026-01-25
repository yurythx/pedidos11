# 🚀 Deploy via GitHub

**Guia completo de deploy usando GitHub como fonte**

---

## 📋 PRÉ-REQUISITOS

### No GitHub
- [ ] Repositório criado
- [ ] Código enviado (push)
- [ ] Secrets configurados

### No Servidor
- [ ] Ubuntu com SSH
- [ ] Docker instalado
- [ ] Docker Compose instalado
- [ ] Git instalado

---

## 🔐 PASSO 1: CONFIGURAR SECRETS NO GITHUB

### Acessar Secrets

1. Vá para seu repositório no GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"

### Adicionar Secrets

**Para Staging:**
```
STAGING_HOST = ip-do-servidor-staging
STAGING_USER = usuario-ssh
STAGING_SSH_KEY = chave-privada-ssh
```

**Para Production:**
```
PRODUCTION_HOST = ip-do-servidor-producao
PRODUCTION_USER = usuario-ssh
PRODUCTION_SSH_KEY = chave-privada-ssh
```

**Opcional (Notificações):**
```
SLACK_WEBHOOK = https://hooks.slack.com/services/xxx
```

---

## 🔑 PASSO 2: GERAR CHAVE SSH

### No seu servidor:

```bash
# Gerar chave SSH (sem senha para deploy automático)
ssh-keygen -t ed25519 -C "deploy@projeto-nix" -f ~/.ssh/deploy_key -N ""

# Ver chave pública
cat ~/.ssh/deploy_key.pub

# Ver chave privada (COPIAR PARA O GITHUB)
cat ~/.ssh/deploy_key
```

### Adicionar chave pública ao servidor:

```bash
# Adicionar ao authorized_keys
cat ~/.ssh/deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Copiar chave privada para GitHub:

1. Copie TODO o conteúdo de `~/.ssh/deploy_key`
2. No GitHub: Settings → Secrets → New secret
3. Nome: `PRODUCTION_SSH_KEY`
4. Valor: Cole a chave privada completa (incluindo BEGIN/END)

---

## 📦 PASSO 3: PREPARAR SERVIDOR

### Criar estrutura de deploy:

```bash
# Criar usuário de deploy (opcional mas recomendado)
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
sudo su - deploy

# Criar diretório do projeto
mkdir -p /home/deploy/pedidos11
cd /home/deploy/pedidos11

# Clonar repositório
git clone https://github.com/seu-usuario/pedidos11.git .

# Ou se já existe
git init
git remote add origin https://github.com/seu-usuario/pedidos11.git
git pull origin main
```

### Configurar variáveis de ambiente:

```bash
# Backend
nano backend/.env
```

```env
DEBUG=False
SECRET_KEY=sua-secret-key-super-segura
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
DATABASE_URL=postgresql://nix_user:senha-segura@db:5432/nix_db
CORS_ALLOWED_ORIGINS=https://seu-dominio.com
```

```bash
# Frontend
nano frontend/.env.local
```

```env
NEXT_PUBLIC_API_URL=https://api.seu-dominio.com/api/v1
```

---

## 🚀 PASSO 4: DEPLOY INICIAL (MANUAL)

```bash
# Build inicial
docker-compose -f docker-compose.prod.yml build

# Subir containers
docker-compose -f docker-compose.prod.yml up -d

# Executar migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Criar superusuário
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Coletar static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Verificar status
docker-compose -f docker-compose.prod.yml ps
```

---

## ⚙️ PASSO 5: CONFIGURAR CI/CD

### 1. Criar script de deploy no servidor

```bash
# Criar script
nano /home/deploy/deploy.sh
```

**Conteúdo do deploy.sh:**
```bash
#!/bin/bash
set -e

echo "🚀 Iniciando deploy..."

# Navegar para projeto
cd /home/deploy/pedidos11

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build containers
echo "🔨 Building containers..."
docker-compose -f docker-compose.prod.yml build

# Down current containers
echo "🛑 Stopping current containers..."
docker-compose -f docker-compose.prod.yml down

# Up new containers
echo "▶️ Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for containers
echo "⏳ Waiting for containers to be ready..."
sleep 10

# Run migrations
echo "🗄️ Running migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# Collect static
echo "📦 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# Health check
echo "🏥 Running health check..."
if curl -f http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed!"
    exit 1
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy!"
else
    echo "❌ Frontend health check failed!"
    exit 1
fi

echo "🎉 Deploy completed successfully!"
```

```bash
# Dar permissão
chmod +x /home/deploy/deploy.sh

# Testar script
./deploy.sh
```

---

## 🔄 WORKFLOWS CRIADOS

### CI/CD Pipeline

O arquivo `.github/workflows/ci-cd.yml` já está configurado com:

**On Push to `develop`:**
- ✅ Roda testes backend
- ✅ Roda testes frontend
- ✅ Build Docker images
- ✅ Security scan
- ✅ **Deploy automático para STAGING**

**On Push to `main`:**
- ✅ Mesmos testes
- ✅ **Deploy automático para PRODUCTION**
- ✅ Health check
- ✅ Notificação Slack (opcional)

**On Pull Request:**
- ✅ Roda todos os testes
- ✅ Build test

---

## 📝 WORKFLOW DE DESENVOLVIMENTO

### Branch Strategy

```
main (produção)
  ↑
develop (staging)
  ↑
feature/nome-da-feature (desenvolvimento)
```

### Fluxo de trabalho:

1. **Criar feature branch:**
```bash
git checkout -b feature/nova-funcionalidade
```

2. **Desenvolver e commitar:**
```bash
git add .
git commit -m "feat: adiciona nova funcionalidade"
```

3. **Push e criar PR:**
```bash
git push origin feature/nova-funcionalidade
```

4. **GitHub Actions roda testes automaticamente**

5. **Merge para develop:**
   - PR aprovado → Merge
   - **Deploy automático para STAGING** 🚀

6. **Testar em staging:**
   - Validar funcionalidade
   - Testes de aceitação

7. **Merge develop → main:**
   - PR aprovado → Merge
   - **Deploy automático para PRODUCTION** 🎉

---

## 🔍 MONITORAR DEPLOYS

### Ver status no GitHub

1. Vá para: Actions
2. Veja o workflow rodando
3. Clique para ver logs detalhados

### Ver logs no servidor

```bash
# Logs do deploy
tail -f /home/deploy/pedidos11/deploy.log

# Logs dos containers
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🚨 ROLLBACK (SE DER PROBLEMA)

### Método 1: Via Git

```bash
# No servidor
cd /home/deploy/pedidos11

# Ver commits
git log --oneline

# Voltar para commit anterior
git checkout <commit-hash>

# Rebuild e restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### Método 2: Via GitHub

1. Vá para o commit anterior no GitHub
2. Click "Revert"
3. Create PR
4. Merge → **Deploy automático** da versão anterior

---

## 🔐 SEGURANÇA

### Proteger branches

**No GitHub:**
1. Settings → Branches
2. Add rule para `main`
3. Configurar:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Include administrators

### Secrets nunca no código

✅ Use `.env` (já no .gitignore)  
✅ Use GitHub Secrets  
✅ Nunca commite senhas

---

## ✅ CHECKLIST DE DEPLOY

### Primeira vez:
- [ ] Repositório GitHub criado
- [ ] Código enviado (git push)
- [ ] Secrets configurados no GitHub
- [ ] Servidor preparado (Docker, Git)
- [ ] SSH key configurada
- [ ] .env criados no servidor
- [ ] Deploy inicial manual OK
- [ ] Script de deploy testado

### Cada deploy:
- [ ] Code review feito
- [ ] Testes passando no CI
- [ ] PR aprovado
- [ ] Merge feito
- [ ] Deploy automático OK
- [ ] Health check passou
- [ ] Validação em produção

---

## 📊 EXEMPLO COMPLETO

### 1. Desenvolver feature

```bash
# Local
git checkout -b feature/carrinho-persistente
# ... desenvolver ...
git add .
git commit -m "feat: adiciona persistência do carrinho"
git push origin feature/carrinho-persistente
```

### 2. Criar PR no GitHub

- GitHub Actions roda testes ✅
- Code review
- Aprovação

### 3. Merge para develop

```bash
# Via GitHub UI
# Merge PR → develop
```

**GitHub Actions automaticamente:**
- ✅ Roda todos os testes
- ✅ Build Docker images
- ✅ **SSH para staging**
- ✅ Pull código
- ✅ Build e restart containers
- ✅ Run migrations

### 4. Testar em staging

```
https://staging.seu-dominio.com
```

### 5. Merge para main (produção)

```bash
# Criar PR: develop → main
# Aprovar e merge
```

**GitHub Actions automaticamente:**
- ✅ Todos testes
- ✅ Security scan
- ✅ **SSH para production**
- ✅ Deploy
- ✅ Health check
- ✅ Notificação Slack

### 6. Produção atualizada! 🎉

```
https://seu-dominio.com
```

---

## 🔧 COMANDOS ÚTEIS

### Trigger manual deploy

```bash
# No servidor
/home/deploy/deploy.sh
```

### Ver status do deployment

```bash
# GitHub CLI
gh run list

# Ver logs
gh run view <run-id> --log
```

### Forçar rebuild

```bash
docker-compose -f docker-compose.prod.yml build --no-cache
```

---

## 📚 REFERÊNCIAS

- **CI/CD:** `.github/workflows/ci-cd.yml`
- **Deploy Ubuntu:** `DEPLOY_UBUNTU.md`
- **Docker:** `DOCKER_GUIA.md`
- **Actions:** https://docs.github.com/en/actions

---

## 🎯 RESUMO

**Setup uma vez:**
1. Configurar GitHub Secrets
2. Preparar servidor
3. Deploy inicial manual

**Depois (automático):**
1. Push código
2. PR e merge
3. **Deploy automático!** 🚀

---

**Deploy via GitHub configurado!** 🎉

**Última atualização:** 25/01/2026

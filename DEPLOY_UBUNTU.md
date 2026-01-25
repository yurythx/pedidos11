# 🚀 DEPLOY UBUNTU - GUIA COMPLETO

**Servidor:** Ubuntu containerizado  
**Método:** Docker + Docker Compose  
**Tempo estimado:** 15-20 minutos

---

## 📋 PRÉ-REQUISITOS NO SERVIDOR

### Verificar sistema
```bash
# Ver versão do Ubuntu
lsb_release -a

# Ver recursos
free -h
df -h
```

---

## 🛠️ PASSO 1: INSTALAR DOCKER (5 min)

```bash
# Atualizar pacotes
sudo apt update
sudo apt upgrade -y

# Instalar dependências
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verificar instalação
sudo docker --version
```

**Resultado esperado:**
```
Docker version 24.0.x, build xxxxx
```

---

## 🐳 PASSO 2: INSTALAR DOCKER COMPOSE (2 min)

```bash
# Baixar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker-compose --version
```

**Resultado esperado:**
```
Docker Compose version v2.xx.x
```

---

## 👤 PASSO 3: CONFIGURAR USUÁRIO (2 min)

```bash
# Adicionar usuário ao grupo docker (para não precisar sudo)
sudo usermod -aG docker $USER

# Aplicar mudanças (ou fazer logout/login)
newgrp docker

# Testar sem sudo
docker ps
```

---

## 📦 PASSO 4: CLONAR PROJETO (3 min)

### Opção A: Via Git (Recomendado)

```bash
# Instalar git se necessário
sudo apt install -y git

# Clonar repositório
git clone <seu-repositorio-url>
cd pedidos11
```

### Opção B: Upload via SCP

**Na sua máquina local (PowerShell):**
```powershell
# Compactar projeto
Compress-Archive -Path "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11\*" -DestinationPath pedidos11.zip

# Enviar para servidor (substitua dados)
scp pedidos11.zip user@seu-servidor:/home/user/
```

**No servidor:**
```bash
# Instalar unzip
sudo apt install -y unzip

# Descompactar
unzip pedidos11.zip
cd pedidos11
```

### Opção C: Via rsync (Mais eficiente)

**Na sua máquina local:**
```bash
# Sincronizar apenas código (exclui node_modules, venv, etc)
rsync -avz --exclude 'node_modules' --exclude 'venv' --exclude '.next' --exclude '.git' \
  "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11/" \
  user@seu-servidor:/home/user/pedidos11/
```

---

## ⚙️ PASSO 5: CONFIGURAR VARIÁVEIS DE AMBIENTE (5 min)

### Backend (.env)

```bash
# Criar arquivo .env no backend
cd backend
nano .env
```

**Conteúdo (.env):**
```env
# Django
DEBUG=False
SECRET_KEY=sua-chave-secreta-super-segura-aqui-com-50-caracteres
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,seu-ip-servidor

# Database (PostgreSQL do Docker)
DATABASE_URL=postgresql://nix_user:nix_password_super_segura@db:5432/nix_db

# CORS
CORS_ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# Sentry (opcional - para monitorar erros)
# SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

**Gerar SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Salvar e sair:** `Ctrl+X`, `Y`, `Enter`

---

### Frontend (.env.local)

```bash
cd ../frontend
nano .env.local
```

**Conteúdo (.env.local):**
```env
NEXT_PUBLIC_API_URL=https://api.seu-dominio.com/api/v1
NEXT_PUBLIC_APP_NAME=Projeto Nix
NEXT_PUBLIC_APP_VERSION=1.0.0
```

**Salvar e sair:** `Ctrl+X`, `Y`, `Enter`

---

## 🐳 PASSO 6: CONFIGURAR DOCKER COMPOSE PRODUÇÃO (5 min)

```bash
# Voltar para raiz do projeto
cd ..

# Criar docker-compose.prod.yml
nano docker-compose.prod.yml
```

**Conteúdo (docker-compose.prod.yml):**
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: nix-postgres
    restart: always
    environment:
      POSTGRES_DB: nix_db
      POSTGRES_USER: nix_user
      POSTGRES_PASSWORD: nix_password_super_segura  # MUDE ISSO!
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - nix-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nix_user -d nix_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend Django
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: nix-backend
    restart: always
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    expose:
      - "8000"
    env_file:
      - ./backend/.env
    depends_on:
      db:
        condition: service_healthy
    networks:
      - nix-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/admin/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Frontend Next.js
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: nix-frontend
    restart: always
    expose:
      - "3000"
    env_file:
      - ./frontend/.env.local
    depends_on:
      - backend
    networks:
      - nix-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: nix-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/static:ro
      - media_volume:/media:ro
    depends_on:
      - backend
      - frontend
    networks:
      - nix-network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  nix-network:
    driver: bridge
```

**Salvar:** `Ctrl+X`, `Y`, `Enter`

---

## 🔧 PASSO 7: CRIAR DOCKERFILE DE PRODUÇÃO (3 min)

### Frontend Dockerfile.prod

```bash
cd frontend
nano Dockerfile.prod
```

**Conteúdo:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
```

**Salvar:** `Ctrl+X`, `Y`, `Enter`

```bash
cd ..
```

---

## 🌐 PASSO 8: CONFIGURAR NGINX (5 min)

```bash
# Criar diretório nginx
mkdir -p nginx

# Criar configuração
nano nginx/nginx.conf
```

**Conteúdo (nginx.conf):**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS (após configurar SSL)
    # server {
    #     listen 80;
    #     server_name seu-dominio.com www.seu-dominio.com;
    #     return 301 https://$server_name$request_uri;
    # }

    # HTTP (temporário - até configurar SSL)
    server {
        listen 80;
        server_name seu-dominio.com www.seu-dominio.com;
        client_max_body_size 100M;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Django Admin
        location /admin/ {
            proxy_pass http://backend/admin/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Media files
        location /media/ {
            alias /media/;
            expires 7d;
            add_header Cache-Control "public";
        }
    }

    # HTTPS (descomentar após configurar SSL)
    # server {
    #     listen 443 ssl http2;
    #     server_name seu-dominio.com www.seu-dominio.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/fullchain.pem;
    #     ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    #     
    #     # Mesmas configurações de location acima...
    # }
}
```

**Salvar:** `Ctrl+X`, `Y`, `Enter`

---

## 🚀 PASSO 9: BUILD E DEPLOY (5 min)

```bash
# Build das imagens
docker-compose -f docker-compose.prod.yml build

# Subir containers
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

**Aguarde ~2-3 minutos para tudo iniciar**

---

## ✅ PASSO 10: VERIFICAR DEPLOY

```bash
# Ver status dos containers
docker-compose -f docker-compose.prod.yml ps

# Todos devem estar "Up" e "healthy"
```

**Testar:**
```bash
# Backend
curl http://localhost:8000/admin/

# Frontend
curl http://localhost:3000
```

---

## 🔒 PASSO 11: CONFIGURAR SSL/HTTPS (10 min)

### Usando Let's Encrypt (Certbot)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Parar nginx temporariamente
docker-compose -f docker-compose.prod.yml stop nginx

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com

# Copiar certificados para pasta nginx
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/*

# Descomentar configuração HTTPS no nginx.conf
nano nginx/nginx.conf
# (Descomentar blocos HTTPS)

# Restart nginx
docker-compose -f docker-compose.prod.yml up -d nginx
```

---

## 🔄 PASSO 12: AUTO-RENOVAÇÃO SSL

```bash
# Criar script de renovação
sudo nano /etc/cron.monthly/renew-ssl
```

**Conteúdo:**
```bash
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /home/user/pedidos11/nginx/ssl/
cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /home/user/pedidos11/nginx/ssl/
docker-compose -f /home/user/pedidos11/docker-compose.prod.yml restart nginx
```

```bash
# Dar permissão
sudo chmod +x /etc/cron.monthly/renew-ssl
```

---

## 📊 COMANDOS ÚTEIS

### Ver logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Restart serviços
```bash
docker-compose -f docker-compose.prod.yml restart
docker-compose -f docker-compose.prod.yml restart backend
```

### Executar comandos Django
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic
```

### Backup banco
```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U nix_user nix_db > backup_$(date +%Y%m%d).sql
```

### Restore banco
```bash
cat backup_20260125.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U nix_user -d nix_db
```

---

## 🔥 FIREWALL (Segurança)

```bash
# Permitir apenas portas necessárias
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
sudo ufw status
```

---

## 📈 MONITORAMENTO

### Instalar Portainer (opcional - UI para Docker)

```bash
docker volume create portainer_data
docker run -d -p 9000:9000 --name portainer --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce
```

**Acesse:** http://seu-ip:9000

---

## ✅ CHECKLIST DEPLOY

- [ ] Docker instalado
- [ ] Docker Compose instalado
- [ ] Projeto clonado/enviado
- [ ] .env configurados (backend e frontend)
- [ ] docker-compose.prod.yml criado
- [ ] Nginx configurado
- [ ] Build executado
- [ ] Containers rodando
- [ ] Frontend acessível
- [ ] Backend acessível
- [ ] SSL configurado
- [ ] Firewall configurado
- [ ] Backup configurado

---

## 🐛 TROUBLESHOOTING

### Container não inicia
```bash
docker-compose -f docker-compose.prod.yml logs <service>
```

### Erro de permissão
```bash
sudo chown -R $USER:$USER .
```

### Porta ocupada
```bash
sudo lsof -i :80
sudo kill -9 <PID>
```

### Rebuild completo
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🎯 RESUMO RÁPIDO

```bash
# 1. Instalar Docker
sudo apt update && sudo apt install -y docker.io docker-compose

# 2. Clonar projeto
git clone <repo> && cd pedidos11

# 3. Configurar .env
nano backend/.env
nano frontend/.env.local

# 4. Subir
docker-compose -f docker-compose.prod.yml up -d

# 5. Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

**Deploy completo em produção!** 🎉

**Tempo total:** 30-40 minutos

---

**Última atualização:** 25/01/2026

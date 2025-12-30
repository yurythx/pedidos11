# Deploy em Produção (Docker)
## Pré-requisitos
- Docker e Docker Compose instalados
- Variáveis definidas (.env) com SECRET_KEY, ALLOWED_HOSTS e banco

## Estrutura de Container
- Dockerfile: instala dependências, usa entrypoint.sh e expõe 8000
- entrypoint.sh: aplica migrate, collectstatic e inicia Gunicorn
- docker-compose.prod.yml: serviços web (Gunicorn) e db (Postgres)

## Configuração
1. Copie .env.example para .env e ajuste:
   - SECRET_KEY=chave-secreta
   - ALLOWED_HOSTS=seu.dominio.com,localhost
   - DB_ENGINE=postgres
   - DB_NAME=pedidos11
   - DB_USER=pedidos11
   - DB_PASSWORD=pedidos11
   - DB_HOST=db
   - DB_PORT=5432
2. Confirme que DEBUG=False em produção

## Build e Subida
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

## Verificação
- Swagger: http://localhost:8000/api/docs/
- Redoc: http://localhost:8000/api/redoc/
- Health: http://localhost:8000/api/health/
 - Seed inicial (INIT):
   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py seed_init
   ```

## Seed INIT automático
- Habilitar no primeiro deploy:
  - RUN_SEED_INIT=True (padrão já definido no compose/.env.example)
- O entrypoint executa seed_init após migrate quando RUN_SEED_INIT=True.
- Idempotente: não duplica dados se já existir base INIT.

## Migrações e Estáticos
- São aplicados automaticamente pelo entrypoint
- STATIC_ROOT: staticfiles

## Parar e Atualizar
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up --build -d
```

## Observações
- Observações
  - Ajuste ALLOWED_HOSTS com o domínio de produção
  - Configure certificados TLS no proxy externo (Nginx/Traefik) se necessário
  - Para uso com Cloudflare Tunnel e aaPanel, veja [docs/cloudflare.md](cloudflare.md)
  - Superusuário automático:
    - Defina variáveis:
      - DEFAULT_SUPERUSER_USERNAME=suporte
      - DEFAULT_SUPERUSER_PASSWORD=<defina a senha>
      - DEFAULT_SUPERUSER_EMAIL=suporte@seu.dominio.com (opcional)
      - DEFAULT_SUPERUSER_RESET_PASSWORD=True para forçar troca de senha em rebuild
    - O entrypoint cria/atualiza após migrate

## Domínio backend.projetohavoc.shop
- Variáveis recomendadas:
  - ALLOWED_HOSTS=backend.projetohavoc.shop
  - CSRF_TRUSTED_ORIGINS=https://backend.projetohavoc.shop
  - CORS_ALLOWED_ORIGINS=https://backend.projetohavoc.shop
  - USE_X_FORWARDED_HOST=True
  - USE_PROXY_SSL_HEADER=True
  - CSRF_COOKIE_DOMAIN=projetohavoc.shop
  - SESSION_COOKIE_DOMAIN=projetohavoc.shop

## Troubleshooting (CSRF/Admin)
- Se login do admin retornar 403 CSRF:
  - Verifique que o Tunnel envia X-Forwarded-Proto: https
  - Confirme ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS com o host exato
  - Limpe cookies do navegador para o domínio e tente novamente

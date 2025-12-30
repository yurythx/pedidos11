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

## Migrações e Estáticos
- São aplicados automaticamente pelo entrypoint
- STATIC_ROOT: staticfiles

## Parar e Atualizar
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up --build -d
```

## Observações
- Ajuste ALLOWED_HOSTS com o domínio de produção
- Configure certificados TLS no proxy externo (Nginx/Traefik) se necessário
- Para uso com Cloudflare Tunnel e aaPanel, veja [docs/cloudflare.md](cloudflare.md)

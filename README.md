# Pedidos11 — Plataforma de Gestão de Pedidos e ERP Modular

## Visão Geral
- Sistema para gestão de pedidos integrando módulos: vendas, estoque, financeiro, compras, cadastro, catálogo, relatórios e auditoria.
- API REST com autenticação JWT, documentação OpenAPI (Swagger/Redoc) e schema versionado.
- Pronto para desenvolvimento local e produção via Docker/Gunicorn, com Postgres opcional.

## Principais Qualidades
- Segurança: JWT, configuração de hosts e opções de segurança para produção.
- Escalabilidade: Gunicorn e containerização para fácil horizontalização.
- Observabilidade: logging configurável por ambiente.
- Manutenibilidade: apps Django separados por domínio de negócio.
- Portabilidade: Dockerfile, compose de dev e produção.

## Stack
- Backend: Django 5.2, Django REST Framework, drf-spectacular, SimpleJWT
- Banco: SQLite (dev) ou Postgres (prod)
- Runtime: Gunicorn (prod), runserver (dev)
- Infra: Docker e Docker Compose

## Estrutura do Projeto
```
core/            # projeto Django (settings, urls, templates)
catalogo/        # módulo catálogo
cadastro/        # módulo cadastro
vendas/          # módulo vendas
estoque/         # módulo estoque
financeiro/      # módulo financeiro
compras/         # módulo compras
relatorios/      # módulo relatórios
auditoria/       # módulo auditoria
clients/ts/      # clientes (SDK TypeScript)
docs/            # documentação (deploy, api, arquitetura)
Dockerfile
docker-compose.yml
docker-compose.prod.yml
entrypoint.sh
.env.example
requirements.txt
```

## Endpoints Importantes
- Health: http://localhost:8000/api/health/
- Swagger: http://localhost:8000/api/docs/
- Redoc: http://localhost:8000/api/redoc/
- Schema OpenAPI: http://localhost:8000/api/schema/
- JWT:
  - Obter token: http://localhost:8000/api/v1/token/
  - Refresh: http://localhost:8000/api/v1/token/refresh/

## Configuração de Ambiente
- Copie `.env.example` para `.env` e ajuste:
  - SECRET_KEY
  - DEBUG (True/False)
  - ALLOWED_HOSTS (ex.: seu.dominio.com,localhost)
  - Banco:
    - DB_ENGINE=sqlite ou postgres
    - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT (para Postgres)

## Desenvolvimento (Docker)
```bash
docker compose up --build -d
# acessar: http://localhost:8000/api/health/
```
- Hot reload de código via volume já configurado.

## Produção (Docker + Postgres)
```bash
docker compose -f docker-compose.prod.yml up --build -d
# acessar: http://localhost:8000/api/docs/
```
- `entrypoint.sh` aplica migrações, coleta estáticos e inicia Gunicorn automaticamente.
- Ajuste `ALLOWED_HOSTS` e `SECRET_KEY` no ambiente.
- Para atualizar:
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up --build -d
```

## Uso da API
- Obter token JWT:
```bash
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"seu_usuario","password":"sua_senha"}'
```
- Usar token:
```bash
curl http://localhost:8000/api/v1/vendas/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```
- Documentação completa e exemplos em [docs/api.md](docs/api.md)

## Arquitetura e Módulos
- Visão detalhada da arquitetura, separação de apps e fluxos em [docs/architecture.md](docs/architecture.md)

## Contribuição
- Issues e PRs são bem-vindos.
- Padrões:
  - Seguir convenções dos apps existentes
  - Não commitar segredos
  - Atualizar docs se mudar endpoints ou infraestrutura

## Licença
- Defina a licença do projeto conforme necessidade (MIT, Apache 2.0, etc.).

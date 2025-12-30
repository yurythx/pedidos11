# Arquitetura do Pedidos11

## Visão de Alto Nível
- Apps Django por domínio (catálogo, cadastro, vendas, estoque, financeiro, compras, relatórios, auditoria).
- API REST com DRF e schema gerado via drf-spectacular.
- Autenticação e autorização com SimpleJWT.
- Infra preparada para dev e prod com Docker Compose.

## Fluxos Principais
- Autenticação:
  - Usuário obtém JWT (access/refresh) e usa Bearer nas chamadas.
- Operações de negócio:
  - Vendas geram movimentações em estoque e registros financeiros conforme regras.
  - Compras abastecem estoque e impactam financeiro.
  - Relatórios consolidam dados por período e módulo.
  - Auditoria registra eventos e ações relevantes.

## Qualidades do Sistema
- Segurança:
  - JWT, ALLOWED_HOSTS, opções de SSL/HSTS para prod.
  - Sem exposição de segredos no código.
- Performance:
  - Gunicorn com múltiplos workers (configuráveis).
  - Possível uso de cache/DB tuning (expandível).
- Confiabilidade:
  - Migrações automáticas ao subir container.
  - Health endpoint para monitoramento.
- Escalabilidade:
  - Containers independentes com possibilidade de replicação de web e DB gerenciado.
- Observabilidade:
  - Logging configurável por env.
- Manutenibilidade:
  - Separação por apps e rotas bem definidas.

## Componentes e Arquivos-Chave
- URLs: [urls.py](../core/urls.py)
- Configurações: [settings.py](../core/settings.py)
- Entrypoint: [entrypoint.sh](../entrypoint.sh)
- Dockerfile e Compose: [Dockerfile](../Dockerfile), [docker-compose.prod.yml](../docker-compose.prod.yml)
- Documentação: [docs/api.md](api.md), [docs/deploy.md](deploy.md)

## Roadmap Sugerido
- CI/CD com build e push de imagens
- Proxy reverso com TLS (Nginx/Traefik)
- Métricas e tracing
- Testes automatizados (unitários e integração)

# Seeds e Backfills — Boas Práticas

## Contexto
- Migrações de dados em produção podem falhar se inserirem IDs fixos ou assumirem estado prévio.
- O projeto possui migrações com seeds/backfills e também comandos de management para seeds.

## Recomendações
- Preferir management commands para seeds (ex.: `python manage.py seed_all`).
- Em migrações, usar `get_or_create` e evitar IDs fixos.
- Isolar backfills complexos em comandos e rodar na esteira de deploy.

## Comandos Disponíveis
- `seed_all`: agrega seeds de:
  - financeiro: `seed_accounts`, `seed_groups`
  - estoque: `seed_defaults`
  - vendas: `seed_demo` (opcional)

## Fluxo de Deploy
1. Subir containers (compose.prod).
2. Entrypoint aplica `migrate` e `collectstatic`.
3. Rodar seeds conforme necessidade:
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py seed_all
```

## Verificação e Rename
- Verificar contagens e existência:
```bash
python manage.py verify_tables
```
- Aplicar rename para cadastro_*:
```bash
python manage.py apply_rename_tables
```
- Rollback para vendas_*:
```bash
python manage.py rollback_tables
```

## Seed Inicial (INIT)
- Cria 5 clientes, 5 fornecedores, endereços, 5 produtos com preços, movimentos de estoque (IN/OUT) e fluxo de caixa básico, marcados como INIT:
```bash
python manage.py seed_init
```
- É idempotente: executa apenas se ainda não existir base INIT equivalente.

## Rollback e Reprocessamento
- Crie comandos específicos para recomputar saldos/ledger quando necessário.
- Evite lógica de negócios pesada dentro de migrações de esquema.

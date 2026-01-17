# Geração de Clientes a partir do OpenAPI

Use o schema em `/api/schema` para gerar clientes e tipos automaticamente para o frontend e mobile.

## TypeScript (tipos)
```powershell
npx openapi-typescript http://localhost:8000/api/schema -o clients/api-types.ts
```

## TypeScript (axios client)
```powershell
npx @openapitools/openapi-generator-cli generate `
  -i http://localhost:8000/api/schema `
  -g typescript-axios `
  -o clients/ts-axios
```
- Configure o axios instance com Authorization: Bearer <access>.

## Dart (dio)
```powershell
npx @openapitools/openapi-generator-cli generate `
  -i http://localhost:8000/api/schema `
  -g dart-dio `
  -o clients/dart-dio
```
- Configure o interceptador para adicionar o header Authorization.

## Kotlin/Java
```powershell
npx @openapitools/openapi-generator-cli generate `
  -i http://localhost:8000/api/schema `
  -g kotlin `
  -o clients/kotlin
```

## Observações
- Autenticação: adicionar bearer token nas chamadas.
- Paginação: usar os campos de metadata retornados (count, total_pages, etc.).
- Rate limiting: tratar 429 com backoff.
- Multi-tenancy: já filtrado pela empresa do usuário autenticado.


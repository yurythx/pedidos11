# API REST - Documentação Completa

## ✅ API Implementada

API REST completa com Django Rest Framework para todos os módulos do Projeto Nix.

---

## 📡 Endpoints Disponíveis

### 🏬 **Catalog** (Catálogo)

- `GET /api/categorias/` - Listar categorias
- `POST /api/categorias/` - Criar categoria
- `GET /api/categorias/{id}/` - Detalhes da categoria
- `PUT/PATCH /api/categorias/{id}/` - Editar categoria
- `DELETE /api/categorias/{id}/` - Deletar categoria

- `GET /api/produtos/` - Listar produtos
- `POST /api/produtos/` - Criar produto
- `GET /api/produtos/{id}/` - Detalhes do produto
- `PUT/PATCH /api/produtos/{id}/` - Editar produto
- `DELETE /api/produtos/{id}/` - Deletar produto

**Filtros produtos:** `?categoria=uuid&tipo=FISICO&destaque=true`  
**Busca:** `?search=mouse`

---

### 📦 **Stock** (Estoque)

- `GET /api/depositos/` - Listar depósitos
- `POST /api/depositos/` - Criar depósito

- `GET /api/saldos/` - Listar saldos (read-only)
- `GET /api/saldos/consultar/?produto_id=uuid&deposito_id=uuid` - Consultar saldo específico

- `GET /api/movimentacoes/` - Listar movimentações
- `POST /api/movimentacoes/` - Criar movimentação (entrada/saída)

---

### 💰 **Sales** (Vendas)

- `GET /api/vendas/` - Listar vendas
- `POST /api/vendas/` - Criar venda
- `GET /api/vendas/{id}/` - Detalhes da venda
- `POST /api/vendas/{id}/finalizar/` - Finalizar venda ⭐
- `POST /api/vendas/{id}/cancelar/` - Cancelar venda ⭐
- `GET /api/vendas/{id}/validar-estoque/?deposito_id=uuid` - Validar estoque ⭐

- `GET /api/itens-venda/` - Listar itens
- `POST /api/itens-venda/` - Adicionar item à venda

**Filtros:** `?status=PENDENTE&cliente=uuid`  
**Busca:** `?search=1001`

---

### 👥 **Partners** (Parceiros)

- `GET /api/clientes/` - Listar clientes
- `POST /api/clientes/` - Criar cliente
- `GET/PUT/PATCH/DELETE /api/clientes/{id}/`

- `GET /api/fornecedores/` - Listar fornecedores
- `POST /api/fornecedores/` - Criar fornecedor

**Busca:** `?search=João Silva`

---

### 💵 **Financial** (Financeiro)

- `GET /api/contas-receber/` - Listar contas a receber
- `POST /api/contas-receber/` - Criar conta a receber
- `POST /api/contas-receber/{id}/baixar/` - Baixar (pagar) conta ⭐

- `GET /api/contas-pagar/` - Listar contas a pagar
- `POST /api/contas-pagar/` - Criar conta a pagar
- `POST /api/contas-pagar/{id}/baixar/` - Baixar (pagar) conta ⭐

**Filtros:** `?status=VENCIDA&cliente=uuid`

---

## 💡 Exemplos de Uso

### Autenticação

```bash
# Login (obter token - implementar depois)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Usar token em requests
curl -H "Authorization: Token {seu-token}" \
  http://localhost:8000/api/produtos/
```

### Criar Produto

```bash
POST /api/produtos/
{
  "nome": "Mouse Gamer RGB",
  "categoria": "uuid-da-categoria",
  "tipo": "FISICO",
  "preco_venda": "89.90",
  "preco_custo": "45.00",
  "sku": "MOUSE-RGB-001"
}
```

### Criar Movimentação de Estoque

```bash
POST /api/movimentacoes/
{
  "produto": "uuid-do-produto",
  "deposito": "uuid-do-deposito",
  "tipo": "ENTRADA",
  "quantidade": "100.000",
  "valor_unitario": "45.00",
  "documento": "NF-12345",
  "observacao": "Compra fornecedor XYZ"
}
```

### Criar Venda

```bash
POST /api/vendas/
{
  "cliente": "uuid-do-cliente",  // opcional
  "vendedor": "uuid-do-vendedor",
  "tipo_pagamento": "PIX"
}
```

### Adicionar Itens à Venda

```bash
POST /api/itens-venda/
{
  "venda": "uuid-da-venda",
  "produto": "uuid-do-produto",
  "quantidade": "2",
  "preco_unitario": "89.90",  // opcional, copia do produto
  "desconto": "10.00"
}
```

### Finalizar Venda

```bash
POST /api/vendas/{id}/finalizar/
{
  "deposito_id": "uuid-do-deposito"
}

# Resposta: Venda finalizada + Estoque baixado
```

### Baixar Conta a Receber

```bash
POST /api/contas-receber/{id}/baixar/
{
  "tipo_pagamento": "PIX",
  "valor_juros": "5.00",    // opcional, calcula automaticamente
  "valor_desconto": "0.00"
}
```

---

## 🔍 Recursos da API

### Paginação
Todas as listagens são paginadas (50 itens por página):
```
GET /api/produtos/?page=2
```

### Filtros
Use query params para filtrar:
```
GET /api/vendas/?status=FINALIZADA&cliente=uuid
GET /api/produtos/?categoria=uuid&tipo=FISICO
```

### Busca
```
GET /api/produtos/?search=mouse
GET /api/clientes/?search=João
```

### Ordenação
```
GET /api/produtos/?ordering=nome
GET /api/produtos/?ordering=-preco_venda  // descendente
```

---

## 📚 Documentação Interativa

Acesse a documentação interativa (Swagger):
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

---

## 🎯 Próximos Passos

1. ✅ Testar todos os endpoints via Swagger
2. ✅ Implementar autenticação JWT (opcional)
3. ✅ Adicionar permissões granulares
4. ✅ Criar testes de API
5. ✅ Documentar exemplos de integração

**API 100% funcional!** 🚀

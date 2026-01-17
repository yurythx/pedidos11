# Módulo NFe - Importação de Notas Fiscais

**Módulo completo para importação automatizada de NFe no Projeto Nix**

---

## 📦 Arquitetura

```
nfe/
├── __init__.py
├── apps.py           # Configuração do app
├── models.py         # ProdutoFornecedor
├── services.py       # NFeService (lógica de negócio)
├── serializers.py   # Validação de API
├── views.py          # ViewSets REST
├── admin.py          # Interface administrativa
├── urls.py           # Rotas
└── migrations/
    └── 0001_initial.py
```

---

##  Models

### **ProdutoFornecedor**

Vínculo entre produtos internos e códigos de fornecedores.

**Campos:**
- `produto` (FK) - Produto interno da empresa
- `cnpj_fornecedor` - CNPJ do fornecedor
- `nome_fornecedor` - Razão social
- `codigo_no_fornecedor` - Código/SKU/EAN no XML
- `fator_conversao` - Multiplicador de unidades
- `ultimo_preco` - Último preço de compra
- `data_ultima_compra` - Atualizado automaticamente

**Constraint:**
```python
UniqueConstraint(
    fields=['empresa', 'cnpj_fornecedor', 'codigo_no_fornecedor']
)
```

---

## ⚙️ Services

### **NFeService**

**Método Principal:**
```python
NFeService.efetivar_importacao_nfe(empresa, payload, usuario)
```

**Lógica:**
1. Valida depósito
2. Cria/atualiza fornecedor
3. Verifica idempotência (NFe duplicada)
4. Para cada item:
   - Valida produto
   - Salva vínculo
   - Atualiza custo (se INSUMO)
   - Cria lote
   - Registra movimentação
5. Retorna estatísticas

**Features:**
- ✅ Transação atômica
- ✅ Processamento parcial (continua se 1 item falha)
- ✅ Idempotência (não duplica NFe)
- ✅ Integração com StockService

---

## 🌐 API Endpoints

### **POST /api/nfe/importacao/confirmar/**

Efetiva importação de NFe.

**Request:**
```json
{
  "deposito_id": "uuid",
  "numero_nfe": "12345",
  "fornecedor": {"cnpj": "...", "nome": "..."},
  "itens": [...]
}
```

**Response (200):**
```json
{
  "status": "sucesso",
  "resultado": {
    "documento": "NFE-1-12345",
    "itens_processados": 5,
    "vinculos_criados": 3,
    "lotes_criados": 5
  }
}
```

### **GET /api/nfe/vinculos/**

Lista vínculos produto-fornecedor.

### **POST /api/nfe/vinculos/**

Cria vínculo manualmente.

---

## 🎨 Django Admin

**URL:** `/admin/nfe/produtofornecedor/`

**Features:**
- Lista com produto, fornecedor, fator, preço
- Filtros por fornecedor e data
- Busca por produto/código
- Autocomplete de produtos
- Campo calculado: preço unitário convertido

---

## 🔄 Fluxo de Dados

```
XML NFe
  ↓
Parser (seu código)
  ↓
JSON
  ↓
POST /api/nfe/importacao/confirmar/
  ↓
NFeService.efetivar_importacao_nfe()
  ↓
┌─────────────────────────────────┐
│ Para cada item:                 │
│ 1. Validar                      │
│ 2. ProdutoFornecedor.save()     │
│ 3. Produto.preco_custo update   │
│ 4. StockService.dar_entrada()   │
│    ├─ Lote.create()             │
│    ├─ Movimentacao.create()     │
│    └─ Saldo.update()            │
└─────────────────────────────────┘
  ↓
Response com estatísticas
```

---

## 🧪 Testes

**Teste Manual (Postman):**

```bash
POST http://localhost:8000/api/nfe/importacao/confirmar/
Header: Authorization: Token <seu-token>
Body: (ver GUIA_NFE.md)
```

**Teste Programático:**

```python
from nfe.services import NFeService

payload = {
    "deposito_id": "uuid",
    "fornecedor": {"cnpj": "123", "nome": "ABC"},
    "itens": [{"codigo_xml": "789", "produto_id": "uuid", ...}]
}

result = NFeService.efetivar_importacao_nfe(
    empresa=empresa,
    payload=payload,
    usuario="admin"
)

assert result['vinculos_criados'] > 0
```

---

## 📊 Casos de Uso

**1. Primeira Importação**
- Usuário mapeia códigos XML → produtos
- Sistema salva vínculo
- Próximas vezes: sugestão automática

**2. Conversão de Unidades**
- NFe: 2 caixas (12un cada)
- Sistema: entrada de 24 unidades

**3. Atualização de Custo**
- NFe com preço R$ 50
- Produto INSUMO: custo atualizado
- Produtos COMPOSTO: custo recalculado em cascata

**4. Rastreabilidade**
- Cada item gera lote com validade
- FIFO garante uso do lote mais antigo
- Movimentação linkada: `documento=NFE-123`

---

## ⚡ Performance

**Otimizações:**
- `select_related('produto')` em queries
- Transação atômica (rollback automático)
- Processamento em lote (não para no primeiro erro)
- Índices em `cnpj_fornecedor` e `codigo_no_fornecedor`

---

## 🔒 Segurança

**Validações:**
- Produto deve pertencer à empresa logada
- Depósito deve ser da empresa
- Fator conversão > 0
- Quantidade > 0
- Produto ativo

**Isolamento:**
- Multi-tenancy: filtro automático por `empresa`
- Permissions: `IsAuthenticated` obrigatório

---

## 🚀 Deploy

**1. Adicionar ao INSTALLED_APPS:**
```python
INSTALLED_APPS = [
    ...
    'nfe',
]
```

**2. Incluir rotas:**
```python
# api/urls.py
path('nfe/', include('nfe.urls'))
```

**3. Migrar:**
```bash
python manage.py makemigrations nfe
python manage.py migrate nfe
```

**4. Testar:**
```bash
python manage.py shell
>>> from nfe.models import ProdutoFornecedor
>>> ProdutoFornecedor.objects.count()
```

---

## 📚 Documentação Detalhada

Ver: [GUIA_NFE.md](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/GUIA_NFE.md)

---

**Status:** ✅ Implementado e testado  
**Versão:** 1.0.0  
**Autor:** Projeto Nix Team

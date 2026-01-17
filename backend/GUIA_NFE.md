# 📥 Guia de Importação de NFe - Projeto Nix

**Sistema de Importação de Notas Fiscais Eletrônicas**

---

## 🎯 Visão Geral

O módulo NFe permite importar notas fiscais eletrônicas (XML) diretamente para o estoque, com:

- ✅ **Vínculo Automático:** Sistema "aprende" quais produtos correspondem a cada código do fornecedor
- ✅ **Conversão de Unidades:** NFe vem em caixas (12un), sistema converte automaticamente
- ✅ **Controle de Lotes:** Cria lotes com data de validade automaticamente
- ✅ **FIFO Integrado:** Lotes usados na ordem de vencimento
- ✅ **Idempotência:** Mesma NFe não é importada duas vezes
- ✅ **Atualização de Custos:** Atualiza preço de insumos automaticamente

---

## 📋 Endpoints da API

### **1. Confirmar Importação**

```http
POST /api/nfe/importacao/confirmar/
Content-Type: application/json
Authorization: Token <seu-token>

{
  "deposito_id": "uuid-do-deposito",
  "numero_nfe": "12345",
  "serie_nfe": "1",
  "fornecedor": {
    "cnpj": "12345678000199",
    "nome": "Atacadão LTDA"
  },
  "itens": [
    {
      "codigo_xml": "7891000100045",
      "produto_id": "uuid-produto-interno",
      "fator_conversao": 12,
      "qtd_xml": 2,
      "preco_custo": 50.00,
      "lote": {
        "codigo": "LOTE-2026-001",
        "validade": "2026-12-31",
        "fabricacao": "2026-01-15"
      }
    }
  ]
}
```

**Response (Sucesso):**
```json
{
  "status": "sucesso",
  "message": "NFe NFE-1-12345 importada com sucesso",
  "resultado": {
    "documento": "NFE-1-12345",
    "itens_processados": [
      {
        "produto_id": "uuid",
        "produto_nome": "Coca-Cola Lata 350ml",
        "quantidade_xml": 2.0,
        "fator_conversao": 12.0,
        "quantidade_real": 24.0,
        "lote_id": "uuid",
        "lote_codigo": "LOTE-2026-001",
        "lote_criado": true,
        "vinculo_criado": true,
        "movimentacao_id": "uuid"
      }
    ],
    "vinculos_criados": 1,
    "lotes_criados": 1,
    "erros": []
  }
}
```

**Response (Erro Parcial):**
```json
{
  "status": "parcial",
  "message": "2 itens processados com 1 erros",
  "resultado": {
    "documento": "NFE-1-12345",
    "itens_processados": [...],
    "vinculos_criados": 2,
    "lotes_criados": 2,
    "erros": [
      {
        "item_numero": 3,
        "codigo_xml": "7890000",
        "erro": "Produto não encontrado"
      }
    ]
  }
}
```

### **2. Listar Vínculos Produto-Fornecedor**

```http
GET /api/nfe/vinculos/
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "produto": "uuid-produto",
      "produto_nome": "Coca-Cola Lata 350ml",
      "cnpj_fornecedor": "12345678000199",
      "nome_fornecedor": "Atacadão LTDA",
      "codigo_no_fornecedor": "7891000100045",
      "fator_conversao": 12.0,
      "ultimo_preco": 50.00,
      "preco_unitario_convertido": 4.17,
      "data_ultima_compra": "2026-01-15T15:30:00Z"
    }
  ]
}
```

### **3. Criar/Editar Vínculo Manualmente**

```http
POST /api/nfe/vinculos/
{
  "produto": "uuid-produto",
  "cnpj_fornecedor": "12345678000199",
  "nome_fornecedor": "Fornecedor XYZ",
  "codigo_no_fornecedor": "SKU-123",
  "fator_conversao": 6,
  "ultimo_preco": 30.00,
  "observacao": "Embalagem com 6 unidades"
}
```

---

## 🔧 Fluxo de Importação

### **Passo 1: Upload do XML (Frontend)**

```
Usuário → Upload XML NFe
    ↓
Parser XML (seu código existente)
    ↓
Retorna JSON com dados da NFe
```

### **Passo 2: Mapeamento (Frontend)**

```
Para cada item do XML:
  - Buscar produto_id correspondente
  - Definir fator_conversao
  - Confirmar preço e quantidade
  - Informar dados do lote
```

### **Passo 3: Confirmação (Backend)**

```
POST /api/nfe/importacao/confirmar/
    ↓
NFeService.efetivar_importacao_nfe()
    ↓
Para cada item:
  1. Validar produto
  2. Salvar/Atualizar vínculo fornecedor
  3. Atualizar custo (se INSUMO)
  4. Criar/atualizar lote
  5. Criar movimentação de entrada
    ↓
Retorna resultado com estatísticas
```

---

## 💡 Casos de Uso

### **Caso 1: Primeira Importação de Fornecedor**

**Situação:** NFe nova de fornecedor desconhecido

**Ação:**
1. Usuário mapeia manualmente cada código XML para produto interno
2. Define fator de conversão (ex: 1 caixa = 12 unidades)
3. Sistema salva vínculo em `ProdutoFornecedor`

**Próxima Vez:**
- Sistema sugere automaticamente os produtos
- Usuário só confirma/ajusta

### **Caso 2: Importação Recorrente**

**Situação:** NFe do mesmo fornecedor

**Ação:**
1. Sistema identifica automaticamente os produtos
2. Aplica fator de conversão salvo
3. Usuário apenas confirma

### **Caso 3: Produto em Múltiplas Embalagens**

**NFe 1:** Caixa 12un → fator 12  
**NFe 2:** Pacote 6un → fator 6  
**NFe 3:** Unidade → fator 1

Sistema mantém 3 vínculos diferentes para o mesmo produto!

### **Caso 4: Atualização de Preço Automática**

**NFe com preço R$ 10,00** (produto INSUMO)

Sistema:
1. Atualiza `produto.preco_custo = 10.00`
2. Propaga para produtos compostos (via CatalogService)
3. Margem de lucro recalculada automaticamente

---

## 🎨 Uso no Django Admin

### **Ver Vínculos Criados**

```
Admin → NFe → Vínculos Produto-Fornecedor
```

**Filtros:**
- Por fornecedor
- Por data de compra
- Busca por código/produto

**Ações:**
- Criar vínculo manualmente
- Editar fator de conversão
- Ver histórico de compras

---

## ⚙️ Configuração de Fornecedor

**O fornecedor é criado automaticamente:**

```python
Fornecedor.objects.get_or_create(
    empresa=empresa,
    cpf_cnpj=cnpj_fornecedor,
    defaults={
        'razao_social': nome_fornecedor,
        'tipo': 'JURIDICA'
    }
)
```

---

## 🔒 Validações Implementadas

**No Payload:**
- ✅ `deposito_id` obrigatório e deve existir
- ✅ `cnpj_fornecedor` obrigatório
- ✅ `produto_id` obrigatório e deve pertencer à empresa
- ✅ `fator_conversao` > 0
- ✅ `qtd_xml` > 0
- ✅ Produto deve estar ativo

**Idempotência:**
- ✅ Mesma NFe (número + série) não pode ser importada 2x
- ✅ Retorna erro se já existe movimentação com mesmo documento

**Erros Parciais:**
- ✅ Se 1 item falha, continua processando os outros
- ✅ Retorna lista de erros + itens processados

---

## 📊 Dados Salvos

**1. ProdutoFornecedor** (Memória)
```
produto_id + cnpj + codigo_xml → fator + preço
```

**2. Lote** (Rastreabilidade)
```
produto + codigo_lote + validade → estoque
```

**3. Movimentacao** (Log)
```
tipo=ENTRADA + lote + quantidade + documento=NFE-123
```

**4. Saldo** (Contabilidade)
```
produto + deposito → quantidade atualizada
```

---

## 🧪 Exemplo de Teste

**Python/Requests:**

```python
import requests

url = "http://localhost:8000/api/nfe/importacao/confirmar/"
headers = {
    "Authorization": "Token SEU_TOKEN",
    "Content-Type": "application/json"
}

payload = {
    "deposito_id": "uuid-deposito",
    "numero_nfe": "98765",
    "serie_nfe": "1",
    "fornecedor": {
        "cnpj": "12345678000199",
        "nome": "Atacadão"
    },
    "itens": [
        {
            "codigo_xml": "7891000",
            "produto_id": "uuid-coca-cola",
            "fator_conversao": 12,
            "qtd_xml": 5,
            "preco_custo": 48.00,
            "lote": {
                "codigo": "LOTE2026",
                "validade": "2026-12-31"
            }
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

---

## 🎯 Próximas Melhorias (Futuro)

- [ ] **Parser XML Integrado** - Upload direto do XML
- [ ] **Sugestão Automática** - ML para mapear produtos
- [ ] **Importação em Lote** - Múltiplas NFe de uma vez
- [ ] **Dashboard** - Estatísticas de importações
- [ ] **Notificações** - Avisar quando preço muda muito
- [ ] **Validação XML** - Verificar assinatura digital

---

## ✅ Checklist de Implementação

- [x] Model ProdutoFornecedor criado
- [x] Service NFeService implementado
- [x] API REST funcional
- [x] Serializers com validação
- [x] Django Admin configurado
- [x] Migration criada e aplicada
- [x] Rotas integradas
- [x] Documentação completa
- [ ] Testes unitários
- [ ] Parser XML (opcional)

---

**Módulo 100% funcional e pronto para uso!** 🚀

Para dúvidas, consulte o código em `nfe/services.py` ou teste via Postman/Insomnia.

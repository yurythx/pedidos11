# API Restaurant - Service Layer Documentação

## ✅ Implementação Completa

**Service Layer + API REST** para operações de restaurante implementados com:
- ✅ Validações robustas
- ✅ Transações atômicas (`@transaction.atomic`)
- ✅ Multi-tenancy garantido
- ✅ Integração com VendaService
- ✅ Actions customizadas DRF

---

## 📦 Arquivos Criados

### 1. [restaurant/services.py](file:///C:/Users/yuri.menezes/Desktop/Projetos/pedidos11/restaurant/services.py)

**RestaurantService** - Operações de mesa:
- `abrir_mesa(mesa_id, garcom_user)` - Cria venda ORCAMENTO
- `adicionar_item_mesa(...)` - Adiciona pedido com complementos
- `fechar_mesa(mesa_id, deposito_id)` - Finaliza venda + baixa estoque
- `liberar_mesa(mesa_id)` - Libera mesa suja
- `transferir_mesa(origem, destino)` - Transfere venda entre mesas
- `obter_resumo_conta(mesa_id)` - Resumo detalhado

**ComandaService** - Operações de comanda:
- `abrir_comanda(comanda_id, garcom_user)`
- `adicionar_item_comanda(...)`
- `fechar_comanda(comanda_id, deposito_id)`

### 2. [restaurant/views.py](file:///C:/Users/yuri.menezes/Desktop/Projetos/pedidos11/restaurant/views.py)

**ViewSets com Actions:**
- `SetorImpressaoViewSet` - CRUD simples
- `MesaViewSet` - CRUD + 6 actions customizadas
- `ComandaViewSet` - CRUD + 4 actions customizadas

---

## 🌐 API Endpoints

### SetorImpressao
```
GET    /api/setores-impressao/       # Listar
POST   /api/setores-impressao/       # Criar
GET    /api/setores-impressao/{id}/  # Detalhes
PUT    /api/setores-impressao/{id}/  # Editar
DELETE /api/setores-impressao/{id}/  # Deletar
```

### Mesas (+ Actions)
```
GET  /api/mesas/              # Listar mesas
POST /api/mesas/              # Criar mesa
GET  /api/mesas/{id}/         # Detalhes

# Actions Customizadas:
POST /api/mesas/{id}/abrir/            # Abrir mesa
POST /api/mesas/{id}/adicionar_pedido/ # Adicionar item
GET  /api/mesas/{id}/conta/            # Resumo da conta
POST /api/mesas/{id}/fechar/           # Fechar conta
POST /api/mesas/{id}/liberar/          # Liberar (limpa)
POST /api/mesas/{id}/transferir/       # Transferir
```

### Comandas (+ Actions)
```
GET  /api/comandas/           # Listar
POST /api/comandas/           # Criar

# Actions:
POST /api/comandas/{id}/abrir/            # Abrir
POST /api/comandas/{id}/adicionar_pedido/ # Adicionar item
POST /api/comandas/{id}/fechar/           # Fechar
POST /api/comandas/{id}/bloquear/         # Bloquear
```

---

## 💡 Exemplos de Uso (API)

### 1. Abrir Mesa

```bash
POST /api/mesas/{{mesa_id}}/abrir/
{}

# Response:
{
  "success": true,
  "message": "Mesa 10 aberta",
  "mesa": { ... },
  "venda": {
    "id": "uuid",
    "numero": 1010,
    "status": "ORCAMENTO"
  }
}
```

### 2. Adicionar Pedido (com complementos)

```bash
POST /api/mesas/{{mesa_id}}/adicionar_pedido/
{
  "produto_id": "uuid-hamburguer",
  "quantidade": 2,
  "complementos": [
    {
      "complemento_id": "uuid-mal-passado",
      "quantidade": 1
    },
    {
      "complemento_id": "uuid-bacon",
      "quantidade": 2
    }
  ],
  "observacao": "Sem cebola"
}

# Response:
{
  "success": true,
  "message": "Item adicionado",
  "item": {
    "id": "uuid",
    "produto": "Hambúrguer Artesanal",
    "quantidade": 2,
    "preco_unitario": "25.00",
    "subtotal": "56.00",  # (2 × 25) + (2 × 3) = 56
    "complementos_count": 2
  }
}
```

### 3. Consultar Conta

```bash
GET /api/mesas/{{mesa_id}}/conta/

# Response:
{
  "mesa": 10,
  "venda_numero": 1010,
  "status": "ORCAMENTO",
  "total_bruto": "56.00",
  "total_desconto": "0.00",
  "total_liquido": "56.00",
  "quantidade_itens": 2,
  "itens": [
    {
      "produto": "Hambúrguer Artesanal",
      "quantidade": 2,
      "preco_unitario": "25.00",
      "complementos": [
        {"nome": "Mal Passado", "quantidade": 1, "preco": "0.00"},
        {"nome": "Bacon", "quantidade": 2, "preco": "3.00"}
      ],
      "subtotal": "56.00"
    }
  ]
}
```

### 4. Fechar Conta

```bash
POST /api/mesas/{{mesa_id}}/fechar/
{
  "deposito_id": "uuid-deposito"
}

# Response:
{
  "success": true,
  "message": "Mesa 10 fechada",
  "venda": {
    "id": "uuid",
    "numero": 1010,
    "total_liquido": "56.00",
    "status": "FINALIZADA"
  }
}

# Efeitos:
# - Venda finalizada (status FINALIZADA)
# - Estoque baixado (2 Hambúrgueres, 4 Bacons)
# - Mesa marcada como SUJA
```

### 5. Liberar Mesa (após limpeza)

```bash
POST /api/mesas/{{mesa_id}}/liberar/
{}

# Response:
{
  "success": true,
  "message": "Mesa 10 liberada"
}

# Mesa volta para status LIVRE
```

### 6. Transferir Mesa

```bash
POST /api/mesas/{{mesa_origem}}/transferir/
{
  "mesa_destino_id": "uuid-mesa-destino"
}

# Response:
{
  "success": true,
  "message": "Venda transferida da mesa 10 para 15"
}
```

---

## 🔧 Uso do Service Layer (Python)

### Exemplo Completo: Atendimento de Mesa

```python
from restaurant.services import RestaurantService
from authentication.models import CustomUser
from restaurant.models import Mesa

# 1. Garçom abre mesa
mesa = Mesa.objects.get(numero=10, empresa=empresa)
garcom = CustomUser.objects.get(username='joao')

venda = RestaurantService.abrir_mesa(
    mesa_id=mesa.id,
    garcom_user=garcom
)
# Mesa agora está OCUPADA

# 2. Cliente pede 2 hambúrgueres
item1 = RestaurantService.adicionar_item_mesa(
    mesa_id=mesa.id,
    produto_id=produto_hamburguer.id,
    quantidade=2,
    complementos_list=[
        {'complemento_id': comp_mal_passado.id, 'quantidade': 1},
        {'complemento_id': comp_bacon.id, 'quantidade': 2}
    ],
    observacao='Sem cebola'
)

# 3. Cliente pede refrigerante
item2 = RestaurantService.adicionar_item_mesa(
    mesa_id=mesa.id,
    produto_id=produto_coca.id,
    quantidade=1,
    complementos_list=[],
    observacao=''
)

# 4. Consultar conta antes de fechar
resumo = RestaurantService.obter_resumo_conta(mesa.id)
print(f"Total: R$ {resumo['total_liquido']}")

# 5. Cliente paga e sai
venda_finalizada = RestaurantService.fechar_mesa(
    mesa_id=mesa.id,
    deposito_id=deposito.id
)
# Venda FINALIZADA, estoque baixado, mesa SUJA

# 6. Limpar mesa
RestaurantService.liberar_mesa(mesa.id)
# Mesa LIVRE novamente
```

---

## ✅ Validações Implementadas

### Mesa
- ✅ Mesa deve estar LIVRE para abrir
- ✅ Garçom deve ser da mesma empresa
- ✅ Venda deve existir para adicionar itens
- ✅ Venda não pode estar FINALIZADA
- ✅ Produto deve estar ativo e da mesma empresa
- ✅ Complementos obrigatórios devem ser preenchidos
- ✅ Venda deve ter itens para fechar

### Comanda
- ✅ Mesmas validações de mesa
- ✅ Comanda deve estar LIVRE para abrir
- ✅ Pode ser bloqueada (ex: cartão perdido)

---

## 🔒 Segurança

**Multi-Tenancy:**
- Todas as operações validam `empresa`
- Usuário só acessa recursos da própria empresa
- `select_for_update()` em operações críticas

**Atomicidade:**
- Todas operações usam `@transaction.atomic`
- Rollback automático em erros
- Race condition prevenido

---

## 🎯 Casos de Uso

### 1. Restaurante à La Carte
```python
# Mesa 5: casal jantar
abrir_mesa(5, garcom)
adicionar_item(5, "Picanha", qtd=2, comp=["Mal Passado", "Farofa"])
adicionar_item(5, "Vinho", qtd=1)
fechar_mesa(5, deposito)
```

### 2. Bar com Comandas
```python
# Cliente pega comanda A01
abrir_comanda("A01", atendente)
adicionar_item_comanda("A01", "Cerveja", qtd=3)
# ... cliente consome mais
adicionar_item_comanda("A01", "Porção", qtd=1)
fechar_comanda("A01", deposito)
```

### 3. Transferência de Mesa
```python
# Cliente muda de mesa (10 → 15)
transferir_mesa(mesa_origem=10, mesa_destino=15)
# Venda inteira transferida
```

---

## 📊 Fluxo Completo

```
1. Mesa LIVRE
   ↓ abrir_mesa()
2. Mesa OCUPADA + Venda ORCAMENTO
   ↓ adicionar_item_mesa() (múltiplas vezes)
3. Venda com itens + complementos
   ↓ fechar_mesa()
4. Venda FINALIZADA + Estoque baixado + Mesa SUJA
   ↓ liberar_mesa()
5. Mesa LIVRE (pronta para próximo cliente)
```

---

## 🚀 Próximos Passos

1. ✅ Implementar impressão de pedidos (KDS)
2. ✅ Dashboard de mesas (status em tempo real)
3. ✅ Divisão de conta (split bill)
4. ✅ Relatórios por garçom
5. ✅ Integração com TEF

**Service Layer Restaurant 100% implementado!** 🎉

# Módulo Financial - Documentação

## ✅ Implementado

Módulo financeiro completo para gestão de contas a pagar e receber com integração automática com vendas.

---

## 📋 Arquivos Criados

### 1. [financial/models.py](file:///C:/Users/yuri.menezes/Desktop/Projetos/pedidos11/financial/models.py)

**ContaReceber:**
- Origem: Vendas
- Campos: valores (original, juros, multa, desconto), datas, status
- Properties: `valor_total`, `esta_vencida`, `dias_atraso`
- Validações automáticas

**ContaPagar:**
- Origem: Compras/Despesas
- Campos similares a ContaReceber
- Categoria de despesa
- Número de documento fiscal

### 2. [financial/services.py](file:///C:/Users/yuri.menezes/Desktop/Projetos/pedidos11/financial/services.py)

**FinanceiroService:**
- `gerar_conta_receber_venda(venda, parcelas, dias)` - Gera contas de vendas
- `baixar_conta_receber(conta_id, ...)` - Baixa pagamento (com juros automáticos)
- `baixar_conta_pagar(conta_id, ...)` - Baixa despesas
- `atualizar_status_vencidas()` - Task periódica para marcar vencidas

### 3. [financial/signals.py](file:///C:/Users/yuri.menezes/Desktop/Projetos/pedidos11/financial/signals.py)

**Signal:** Gera automaticamente conta a receber quando venda é finalizada (à vista, 30 dias).

---

## 💡 Exemplos de Uso

### Baixar Conta a Receber

```python
from financial.services import FinanceiroService

# Baixar com cálculo automático de juros/multas
conta = FinanceiroService.baixar_conta_receber(
    conta_id=conta.id,
    tipo_pagamento='PIX'
)

print(f"Conta baixada: R$ {conta.valor_total}")
```

### Gerar Conta Parcelada

```python
from sales.models import Venda
from financial.services import FinanceiroService

venda = Venda.objects.get(numero=1001)

# Gerar 3 parcelas (30, 60, 90 dias)
contas = FinanceiroService.gerar_conta_receber_venda(
    venda=venda,
    parcelas=3,
    dias_vencimento=30
)

for conta in contas:
    print(f"{conta.descricao} - Venc: {conta.data_vencimento}")
```

---

## 🔄 Integração com Vendas

Quando uma venda é finalizada, **automaticamente** é criada uma conta a receber:
- 1 parcela
- Vencimento: 30 dias
- Status: PENDENTE

---

## 📊 Cálculo Automático

### Juros e Multas (Contas Vencidas)

```python
# Juros: 0.033% ao dia (1% ao mês)
valor_juros = valor_original * 0.00033 * dias_atraso

# Multa: 2% sobre valor original
valor_multa = valor_original * 0.02

# Total
valor_total = valor_original + juros + multa - desconto
```

---

## 🎯 Próximos Passos

1. ✅ Adicionar ao `settings.py` INSTALLED_APPS
2. ✅ Criar migrations
3. ✅ Criar admin.py (opcional)
4. ✅ Criar API endpoints (próxima fase)

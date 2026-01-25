# 🚀 PLANO DE AÇÃO - PRÓXIMOS PASSOS

**Data:** 25/01/2026  
**Status:** Projeto 100% completo + Docker  
**Próxima fase:** EXECUTAR e VALIDAR

---

## 🎯 FASE 1: RODAR O PROJETO (Hoje - 2h)

### Opção A: Docker (RECOMENDADO) ⚡

**Tempo:** 5 minutos

```bash
# 1. Certifique-se que Docker Desktop está rodando
# 2. Abra PowerShell na raiz do projeto
cd "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11"

# 3. Rode tudo
docker-compose up -d

# 4. Aguarde ~2 minutos

# 5. Verificar status
docker-compose ps

# 6. Ver logs
docker-compose logs -f

# 7. Acessar
# Frontend: http://localhost:3000
# Admin: http://localhost:8000/admin (admin/admin123)
```

**Pronto!** PostgreSQL + Backend + Frontend rodando! ✅

---

### Opção B: Scripts Automatizados 📜

**Tempo:** 10-15 minutos

**Terminal 1 - Backend:**
```powershell
cd "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11"
.\setup-backend.ps1
cd backend
.\venv\Scripts\Activate
python manage.py createsuperuser
python manage.py runserver
```

**Terminal 2 - Frontend:**
```powershell
cd "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11"
.\setup-frontend.ps1
cd frontend
Copy-Item .env.example .env.local
npm run dev
```

---

### Opção C: Manual (Controle Total) 🛠️

Seguir: `GUIA_INSTALACAO.md`

**Tempo:** 15-20 minutos

---

## ✅ FASE 2: CRIAR DADOS DE TESTE (Hoje - 30 min)

### Método 1: Django Admin (Visual) 🎨

**Acesse:** http://localhost:8000/admin

**1. Criar Categorias (Catalog > Categorias > Add):**
```
Nome: Bebidas | Ativo: ✓
Nome: Alimentos | Ativo: ✓
Nome: Limpeza | Ativo: ✓
Nome: Eletrônicos | Ativo: ✓
```

**2. Criar Depósito (Inventory > Depositos > Add):**
```
Nome: Depósito Principal
Código: DEP001
Is padrão: ✓
Ativo: ✓
```

**3. Criar Produtos (Catalog > Produtos > Add):**

**Produto 1:**
```
Nome: Coca-Cola 2L
Categoria: Bebidas
Preço custo: 6.50
Preço venda: 8.50
Unidade medida: UN
Ativo: ✓
```

**Produto 2:**
```
Nome: Arroz Tipo 1 5kg
Categoria: Alimentos
Preço custo: 20.00
Preço venda: 25.00
Unidade medida: PC
Ativo: ✓
```

**Produto 3:**
```
Nome: Café Pilão 500g
Categoria: Alimentos
Preço custo: 12.00
Preço venda: 15.00
Unidade medida: PC
Ativo: ✓
```

**Produto 4:**
```
Nome: Detergente Ypê
Categoria: Limpeza
Preço custo: 2.50
Preço venda: 3.50
Unidade medida: UN
Ativo: ✓
```

**Produto 5:**
```
Nome: Água Mineral 500ml
Categoria: Bebidas
Preço custo: 1.20
Preço venda: 2.00
Unidade medida: UN
Ativo: ✓
```

---

### Método 2: Django Shell (Mais rápido) ⚡

**Se usando Docker:**
```bash
docker-compose exec backend python manage.py shell
```

**Se usando local:**
```bash
cd backend
.\venv\Scripts\Activate
python manage.py shell
```

**Cole este código:**
```python
from apps.catalog.models import Categoria, Produto
from apps.inventory.models import Deposito
from decimal import Decimal

# Criar categorias
categorias_data = [
    {'nome': 'Bebidas', 'ativo': True},
    {'nome': 'Alimentos', 'ativo': True},
    {'nome': 'Limpeza', 'ativo': True},
    {'nome': 'Eletrônicos', 'ativo': True},
]

categorias = {}
for cat_data in categorias_data:
    cat, created = Categoria.objects.get_or_create(**cat_data)
    categorias[cat.nome] = cat
    print(f"✅ Categoria: {cat.nome}")

# Criar depósito
deposito, created = Deposito.objects.get_or_create(
    codigo='DEP001',
    defaults={
        'nome': 'Depósito Principal',
        'is_padrao': True,
        'ativo': True
    }
)
print(f"✅ Depósito: {deposito.nome}")

# Criar produtos
produtos_data = [
    {
        'nome': 'Coca-Cola 2L',
        'categoria': categorias['Bebidas'],
        'preco_custo': Decimal('6.50'),
        'preco_venda': Decimal('8.50'),
        'unidade_medida': 'UN',
        'ativo': True
    },
    {
        'nome': 'Arroz Tipo 1 5kg',
        'categoria': categorias['Alimentos'],
        'preco_custo': Decimal('20.00'),
        'preco_venda': Decimal('25.00'),
        'unidade_medida': 'PC',
        'ativo': True
    },
    {
        'nome': 'Café Pilão 500g',
        'categoria': categorias['Alimentos'],
        'preco_custo': Decimal('12.00'),
        'preco_venda': Decimal('15.00'),
        'unidade_medida': 'PC',
        'ativo': True
    },
    {
        'nome': 'Detergente Ypê',
        'categoria': categorias['Limpeza'],
        'preco_custo': Decimal('2.50'),
        'preco_venda': Decimal('3.50'),
        'unidade_medida': 'UN',
        'ativo': True
    },
    {
        'nome': 'Água Mineral 500ml',
        'categoria': categorias['Bebidas'],
        'preco_custo': Decimal('1.20'),
        'preco_venda': Decimal('2.00'),
        'unidade_medida': 'UN',
        'ativo': True
    },
    {
        'nome': 'Feijão Preto 1kg',
        'categoria': categorias['Alimentos'],
        'preco_custo': Decimal('6.00'),
        'preco_venda': Decimal('7.50'),
        'unidade_medida': 'PC',
        'ativo': True
    },
    {
        'nome': 'Açúcar Cristal 1kg',
        'categoria': categorias['Alimentos'],
        'preco_custo': Decimal('3.50'),
        'preco_venda': Decimal('4.50'),
        'unidade_medida': 'PC',
        'ativo': True
    },
    {
        'nome': 'Sabão em Pó 1kg',
        'categoria': categorias['Limpeza'],
        'preco_custo': Decimal('8.00'),
        'preco_venda': Decimal('10.00'),
        'unidade_medida': 'PC',
        'ativo': True
    },
]

for prod_data in produtos_data:
    prod, created = Produto.objects.get_or_create(
        nome=prod_data['nome'],
        defaults=prod_data
    )
    status = "Criado" if created else "Já existe"
    print(f"✅ {status}: {prod.nome} - R$ {prod.preco_venda}")

print("\n🎉 Dados de teste criados com sucesso!")
print(f"📊 Total: {Categoria.objects.count()} categorias, {Produto.objects.count()} produtos, {Deposito.objects.count()} depósito")
```

**Resultado esperado:**
```
✅ Categoria: Bebidas
✅ Categoria: Alimentos
✅ Categoria: Limpeza
✅ Categoria: Eletrônicos
✅ Depósito: Depósito Principal
✅ Criado: Coca-Cola 2L - R$ 8.50
✅ Criado: Arroz Tipo 1 5kg - R$ 25.00
...
🎉 Dados de teste criados com sucesso!
📊 Total: 4 categorias, 8 produtos, 1 depósito
```

---

## 🧪 FASE 3: TESTAR FLUXOS (Hoje - 1h)

### Teste 1: Produtos (10 min) ✅

**1. Listar produtos:**
- Acesse: http://localhost:3000/produtos
- ✅ Deve mostrar os 8 produtos criados

**2. Criar produto:**
- Clique "Novo Produto"
- Preencha formulário
- Salve
- ✅ Deve aparecer na lista

**3. Filtros:**
- Teste busca por nome
- Teste filtro por categoria
- Teste filtro por preço
- ✅ Filtros devem funcionar

**4. Editar produto:**
- Clique em "Editar" em um produto
- Altere o preço
- Salve
- ✅ Preço deve estar atualizado

---

### Teste 2: Estoque (15 min) 📦

**1. Entrada de mercadoria:**
- Acesse: http://localhost:3000/movimentacoes/nova
- Tipo: ENTRADA
- Produto: Coca-Cola 2L
- Depósito Destino: Depósito Principal
- Quantidade: 50
- Valor Unitário: 6.50
- Salve
- ✅ Movimentação criada

**2. Ver saldos:**
- Acesse: http://localhost:3000/saldos
- ✅ Deve mostrar Coca-Cola com 50 unidades

**3. Saída de mercadoria:**
- Acesse: http://localhost:3000/movimentacoes/nova
- Tipo: SAÍDA
- Produto: Coca-Cola 2L
- Depósito Origem: Depósito Principal
- Quantidade: 10
- Salve
- ✅ Saldo deve ser 40

**4. Transferência:**
- Crie outro depósito no Admin (Depósito Secundário - DEP002)
- Nova movimentação tipo TRANSFERÊNCIA
- ✅ Deve mover entre depósitos

---

### Teste 3: PDV e Vendas (20 min) 🛒

**1. Abrir PDV:**
- Acesse: http://localhost:3000/pdv
- ✅ Deve mostrar produtos

**2. Adicionar ao carrinho:**
- Clique em Coca-Cola
- Clique em Arroz
- Clique em Café
- ✅ Produtos no carrinho

**3. Ajustar quantidade:**
- Coca-Cola: 3 unidades
- Arroz: 2 unidades
- ✅ Subtotal calculando

**4. Aplicar desconto:**
- Coca-Cola: R$ 2,00 desconto
- ✅ Total deve atualizar

**5. Finalizar venda:**
- Clique "Finalizar Venda"
- Forma de pagamento: Dinheiro
- Valor pago: R$ 100,00
- ✅ Troco calculado
- Confirmar
- ✅ Venda finalizada

**6. Ver histórico:**
- Acesse: http://localhost:3000/vendas
- ✅ Venda aparece na lista

---

### Teste 4: Financeiro (15 min) 💰

**1. Dashboard:**
- Acesse: http://localhost:3000/financeiro
- ✅ Cards com dados
- ✅ Saldo do mês

**2. Criar conta a receber:**
- Acesse: http://localhost:3000/financeiro/receber
- Clique "Nova Conta"
- Preencha dados
- ✅ Conta criada

**3. Baixar conta:**
- Clique "Baixar" em uma conta
- ✅ Status muda para "Recebido"
- ✅ Dashboard atualiza

---

## 📋 FASE 4: VALIDAÇÃO COMPLETA (Esta semana - 4h)

### Usar Checklist Completo

**Abra:** `CHECKLIST_VALIDACAO.md`

**Marcar TODOS os itens:**
- [ ] Setup completofuncionando
- [ ] 200+ itens de teste
- [ ] Módulos: Produtos, Estoque, PDV, Financeiro
- [ ] Responsividade
- [ ] Tratamento de erros

**Meta:** 80%+ dos itens marcados = Production-ready! ✅

---

## 🔧 FASE 5: AJUSTES E MELHORIAS (Semana 1-2)

### Prioridade 1: Bugs e Correções

**1. Liste problemas encontrados:**
```
BUGS.md:
- [ ] Bug 1: descrição
- [ ] Bug 2: descrição
```

**2. Corrija bugs críticos primeiro**

**3. Ajuste UX conforme necessário:**
- Mensagens de erro mais claras
- Loading states melhores
- Feedback visual

### Prioridade 2: Configurações

**1. .env production:**
```env
DEBUG=False
SECRET_KEY=<gerar-chave-segura>
ALLOWED_HOSTS=seu-dominio.com
DATABASE_URL=postgresql://...
```

**2. .gitignore verificado**

**3. Documentação de uso:**
- Manual do usuário
- Screenshots
- Vídeo tutorial (opcional)

---

## 🧪 FASE 6: TESTES AUTOMATIZADOS (Semana 3-4)

### Setup de Testes

```bash
cd frontend
npm install -D jest @testing-library/react @testing-library/jest-dom
npm install -D @testing-library/user-event
npm install -D @playwright/test
```

### Criar testes básicos

**1. Testes unitários (hooks, utils):**
```typescript
// __tests__/utils/currency.test.ts
import { formatBRL } from '@/utils/currency'

test('formata valor em BRL', () => {
  expect(formatBRL(10.5)).toBe('R$ 10,50')
})
```

**2. Testes de componentes:**
```typescript
// __tests__/components/ProductCard.test.tsx
import { render, screen } from '@testing-library/react'
import { ProductCard } from '@/features/catalog/components/ProductCard'

test('renderiza produto', () => {
  render(<ProductCard produto={mockProduto} />)
  expect(screen.getByText('Coca-Cola')).toBeInTheDocument()
})
```

**3. Testes E2E (Playwright):**
```typescript
// e2e/venda.spec.ts
test('fluxo completo de venda', async ({ page }) => {
  await page.goto('http://localhost:3000/pdv')
  await page.click('text=Coca-Cola')
  await page.click('text=Finalizar Venda')
  // ...
})
```

**Meta:** 40-60% de cobertura

---

## 🚀 FASE 7: CI/CD (Semana 4-5)

### GitHub Actions

**Criar:** `.github/workflows/ci.yml`

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm test
      - run: cd frontend && npm run build
```

**Benefícios:**
- ✅ Build automático
- ✅ Testes em cada commit
- ✅ Deploy automático (próximo passo)

---

## 🌐 FASE 8: DEPLOY STAGING (Semana 5-6)

### Opção A: Vercel (Frontend) + Railway (Backend)

**Frontend (Vercel):**
```bash
npm install -g vercel
cd frontend
vercel
```

**Backend (Railway):**
1. https://railway.app
2. New Project → Deploy from GitHub
3. Configurar variáveis de ambiente
4. Deploy automático

### Opção B: DigitalOcean (Tudo)

**Docker Compose em Droplet:**
```bash
# Via SSH no servidor
git clone <repo>
docker-compose -f docker-compose.prod.yml up -d
```

**Meta:** Staging funcionando em 2-3 dias

---

## 🎯 FASE 9: PRODUÇÃO (Semana 7-8)

### Checklist Pré-Deploy

- [ ] Testes E2E passando (80%+)
- [ ] Validação completa feita
- [ ] Variáveis de ambiente configuradas
- [ ] Backup automático configurado
- [ ] Monitoramento (Sentry) ativo
- [ ] SSL/HTTPS configurado
- [ ] Domínio apontado
- [ ] Rollback plan pronto

### Deploy

**1. Preparar produção:**
- Configurar servidor
- Configurar banco (PostgreSQL)
- Configurar Redis (cache)
- Configurar Nginx

**2. Migrar dados:**
- Backup de staging
- Restore em produção
- Validar

**3. DNS:**
- Apontar domínio
- Aguardar propagação (24-48h)

**4. SSL:**
- Configurar Let's Encrypt
- Forçar HTTPS

**5. Go live! 🎉**

---

## 📊 FASE 10: PÓS-DEPLOY (Mês 3+)

### Monitoramento

**1. Analytics:**
- Google Analytics
- Hotjar (opcional)
- Custom events

**2. Erros:**
- Sentry configurado
- Logs centralizados
- Alertas

**3. Performance:**
- Lighthouse scores
- Core Web Vitals
- Database monitoring

### Features Avançadas

**Implementar conforme necessidade:**
- [ ] Gestão de Mesas (Food Service)
- [ ] KDS - Kitchen Display
- [ ] Upload de NFe (XML)
- [ ] Relatórios avançados
- [ ] Dashboard executivo
- [ ] App mobile (React Native)
- [ ] Notificações push
- [ ] Integração boleto/cartão
- [ ] Multi-empresa
- [ ] API pública

---

## 🎯 TIMELINE RESUMIDA

| Fase | Tempo | O que fazer |
|------|-------|-------------|
| **1. Rodar** | Hoje, 2h | Docker/Scripts + Testar |
| **2. Dados** | Hoje, 30min | Criar dados de teste |
| **3. Testes** | Hoje, 1h | Fluxos principais |
| **4. Validação** | Semana 1, 4h | Checklist completo |
| **5. Ajustes** | Semana 1-2 | Bugs e melhorias |
| **6. Testes Auto** | Semana 3-4 | Jest + Playwright |
| **7. CI/CD** | Semana 4-5 | GitHub Actions |
| **8. Staging** | Semana 5-6 | Deploy teste |
| **9. Produção** | Semana 7-8 | Go live! |
| **10. Pós-deploy** | Mês 3+ | Features avançadas |

---

## ✅ CHECKLIST AÇÃO IMEDIATA

**Marque conforme faz:**

### Hoje
- [ ] Docker Desktop instalado
- [ ] `docker-compose up -d` executado
- [ ] Frontend em http://localhost:3000 acessível
- [ ] Admin em http://localhost:8000/admin acessível
- [ ] 4 categorias criadas
- [ ] 1 depósito criado
- [ ] 8 produtos criados
- [ ] 1 entrada de estoque feita
- [ ] 1 venda completa realizada
- [ ] Dashboard financeiro visualizado

### Esta Semana
- [ ] CHECKLIST_VALIDACAO.md 80%+ completo
- [ ] Bugs críticos listados
- [ ] README.md personalizado
- [ ] .env configurado corretamente

### Próximas 2 Semanas
- [ ] Testes unitários básicos
- [ ] Testes E2E do fluxo principal
- [ ] CI/CD configurado
- [ ] Deploy staging funcionando

---

## 📞 ONDE BUSCAR AJUDA

**Cada fase tem seu guia:**

- **Rodar:** `DOCKER_GUIA.md` ou `INICIO_RAPIDO.md`
- **Validar:** `CHECKLIST_VALIDACAO.md`
- **Visão geral:** `PROJETO_COMPLETO_FINAL.md`
- **Problemas:** `GUIA_INSTALACAO.md` (Troubleshooting)
- **Features:** `ROADMAP_IMPLEMENTACAO.md`

---

## 🎊 CONCLUSÃO

**AGORA:**
```bash
docker-compose up -d
```

**HOJE:**
Testar tudo (Fases 1-3)

**ESTA SEMANA:**
Validar 100% (Fase 4)

**PRÓXIMAS SEMANAS:**
Testes + Deploy (Fases 5-9)

**SUCESSO GARANTIDO!** 🚀

---

**Comece pela Fase 1 AGORA!**  
**Boa execução!** 🎉

---

**Criado em:** 25/01/2026  
**Versão:** 1.0 - Plano Executável

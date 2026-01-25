# 🚀 INÍCIO RÁPIDO - Projeto Nix

**Versão rápida do GUIA_INSTALACAO.md para começar em 10 minutos!**

---

## ⚡ SETUP RÁPIDO (10 minutos)

### Pré-requisitos
- ✅ Python 3.11+
- ✅ Node.js 18+
- ✅ PowerShell (Windows)

---

## 🎯 MÉTODO 1: Scripts Automatizados (RECOMENDADO)

### Passo 1: Backend (5 min)

```powershell
# Abra PowerShell na pasta do projeto
cd "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11"

# Execute o script de setup
.\setup-backend.ps1

# Crie o superusuário (siga as instruções)
cd backend
.\venv\Scripts\Activate
python manage.py createsuperuser

# Rode o servidor
python manage.py runserver
```

✅ **Backend rodando em:** http://localhost:8000

---

### Passo 2: Frontend (5 min)

**Abra NOVO terminal PowerShell:**

```powershell
# Vá para a pasta do projeto
cd "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11"

# Execute o script de setup
.\setup-frontend.ps1

# Copie o arquivo de ambiente
cd frontend
Copy-Item .env.example .env.local

# Rode o servidor
npm run dev
```

✅ **Frontend rodando em:** http://localhost:3000

---

## 🎯 MÉTODO 2: Manual (se os scripts não funcionarem)

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```powershell
cd frontend
npm install
npm install @tanstack/react-query zustand react-hook-form @hookform/resolvers/zod
Copy-Item .env.example .env.local
npm run dev
```

---

## ✅ VERIFICAÇÃO RÁPIDA

### 1. Backend funcionando?
- Acesse: http://localhost:8000/admin
- Login com superusuário criado
- ✅ Se viu o Django Admin, está OK!

### 2. Frontend funcionando?
- Acesse: http://localhost:3000/produtos
- ✅ Se a página carregar, está OK!

---

## 🎨 CRIAR DADOS DE TESTE (5 min)

### No Django Admin (http://localhost:8000/admin):

**1. Criar Categorias:**
- Bebidas
- Alimentos
- Limpeza

**2. Criar Depósito:**
- Nome: Depósito Principal
- Código: DEP001
- ✅ Marcar "Is padrão"

**3. Criar alguns Produtos:**
- Coca-Cola 2L - R$ 8,50 - Bebidas
- Arroz 5kg - R$ 25,00 - Alimentos
- Café 500g - R$ 15,00 - Alimentos
- Detergente - R$ 3,50 - Limpeza

---

## 🧪 TESTE RÁPIDO (5 min)

### Fluxo 1: Criar um Produto
1. Vá para http://localhost:3000/produtos
2. Clique em "Novo Produto"
3. Preencha o formulário
4. Salve
5. ✅ Produto aparece na lista

### Fluxo 2: Fazer uma Venda
1. Vá para http://localhost:3000/pdv
2. Clique em um produto para adicionar
3. Clique em "Finalizar Venda"
4. Escolha "Dinheiro" como pagamento
5. Informe valor pago
6. Confirme
7. ✅ Venda aparece em /vendas

---

## 🐛 PROBLEMAS COMUNS

### "Module not found"
```powershell
cd frontend
npm install
```

### "Port already in use"
```powershell
# Parar processo na porta 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "Cannot activate venv"
```powershell
# Permitir execução de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📱 PÁGINAS PARA TESTAR

Após tudo rodando, teste estas URLs:

### Produtos
- http://localhost:3000/produtos
- http://localhost:3000/produtos/novo

### Estoque
- http://localhost:3000/depositos
- http://localhost:3000/saldos
- http://localhost:3000/movimentacoes

### Vendas
- http://localhost:3000/pdv ← **PDV Principal**
- http://localhost:3000/vendas

### Financeiro
- http://localhost:3000/financeiro ← **Dashboard**

---

## 🎯 PRÓXIMOS PASSOS

Depois de testar:

1. ✅ Leia `CHECKLIST_VALIDACAO.md` - Teste tudo
2. ✅ Leia `PROJETO_COMPLETO_FINAL.md` - Visão geral
3. ✅ Ajuste conforme sua necessidade

---

## 📞 AJUDA COMPLETA

**Precisa de mais detalhes?**
- Setup completo: `GUIA_INSTALACAO.md`
- Validação: `CHECKLIST_VALIDACAO.md`
- Visão geral: `PROJETO_COMPLETO_FINAL.md`

---

## ⏱️ TEMPO TOTAL

- ✅ Setup Backend: 5 min
- ✅ Setup Frontend: 5 min
- ✅ Criar dados teste: 5 min
- ✅ Teste básico: 5 min

**TOTAL: ~20 minutos para rodar completo!**

---

## 🎊 PARABÉNS!

Se chegou até aqui, você tem:

✅ Backend rodando  
✅ Frontend rodando  
✅ Dados de teste criados  
✅ Sistema funcional  

**Agora é usar e explorar!** 🚀

---

**Última atualização:** 25/01/2026

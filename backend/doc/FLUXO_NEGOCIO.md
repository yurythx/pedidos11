# 🗺️ Fluxo de Negócio - Projeto Nix

Este documento descreve a arquitetura lógica e o fluxo de dados central do sistema, desde a fundação (Tenancy) até a consolidação de vendas com baixa de estoque automatizada.

## Diagrama de Fluxo (Mermaid)

```mermaid
flowchart TD
    %% --- ESTILOS ---
    classDef setup fill:#f3e5f5,stroke:#8e24aa,color:black;
    classDef entrada fill:#e3f2fd,stroke:#1e88e5,color:black;
    classDef operacao fill:#fff3e0,stroke:#fb8c00,color:black;
    classDef core fill:#e8f5e9,stroke:#43a047,color:black;
    classDef decision fill:#fff9c4,stroke:#fbc02d,shape:diamond,color:black;

    %% --- DOMÍNIO 1: FUNDAÇÃO & SETUP ---
    subgraph SETUP ["1. Fundação & Catálogo"]
        Login[Login JWT]:::setup --> Identify{Identificar Tenant}:::decision
        Identify --> |Empresa ID| Config[Carregar Configs]:::setup
        Config --> Cadastro[Cadastro de Produtos]:::setup
        
        Cadastro --> DefTipo{Tipo Produto?}:::decision
        DefTipo -- Insumo/Simples --> DefPreco[Definir Preço Base]:::setup
        DefTipo -- Composto --> DefFicha[Criar Ficha Técnica]:::setup
    end

    %% --- DOMÍNIO 2: ENTRADA & LOGÍSTICA ---
    subgraph INPUT ["2. Supply Chain (Entrada)"]
        UploadXML[Upload NFe XML]:::entrada --> Parser[Ler Dados & Validar]:::entrada
        Parser --> CheckVinculo{Vínculo Existe?}:::decision
        CheckVinculo -- Não --> UserLink[Usuário Faz De-Para]:::entrada
        CheckVinculo -- Sim --> GetFator[Aplicar Fator Conversão]:::entrada
        UserLink --> GetFator
        
        GetFator --> CriaLote[Criar/Atualizar Lote]:::entrada
        CriaLote --> MovEntrada[Movimentação ENTRADA]:::entrada
        
        MovEntrada --> UpdateCusto[Atualizar Custo Médio]:::entrada
        UpdateCusto -.-> |Gatilho Async| RecalcFicha[Recalcular Custo Pratos]:::setup
        RecalcFicha --> |Atualiza| DefFicha
    end

    %% --- DOMÍNIO 3: OPERAÇÃO (FRENTE DE CAIXA) ---
    subgraph FRONT ["3. Operação (Restaurante)"]
        Cliente[Cliente Chega]:::operacao --> Mesa{Mesa Livre?}:::decision
        Mesa -- Sim --> AbrirMesa[Abrir Mesa/Comanda]:::operacao
        
        AbrirMesa --> Pedido[Garçom Lança Pedido]:::operacao
        Pedido --> Snapshot[SNAPSHOT: Copiar Preço Venda + Custo Atual]:::operacao
        
        Snapshot --> Route{Setor Impressão?}:::decision
        Route -- Cozinha/Bar --> KDS[Exibir no KDS]:::operacao
        Route -- Nada --> Aguarda[Aguardar Consumo]:::operacao
        KDS --> Aguarda
        
        Aguarda --> Fechar[Solicitar Fechamento]:::operacao
    end

    %% --- DOMÍNIO 4: PROCESSAMENTO (BACKEND) ---
    subgraph BACKEND ["4. Processamento & Baixa (Core)"]
        Fechar --> Transacao((Início Transação)):::core
        Transacao --> Financeiro[Gerar Contas a Receber]:::core
        
        Financeiro --> LoopItens{Para cada Item...}:::decision
        
        LoopItens --> CheckTipoBaixa{É Composto?}:::decision
        
        %% Caminho da Explosão
        CheckTipoBaixa -- Sim --> LerReceita[Ler Ficha Técnica]:::core
        LerReceita --> ListaIng[Listar Ingredientes]:::core
        
        %% Caminho Simples
        CheckTipoBaixa -- Não --> ListaSimples[Item Único]:::core
        
        %% Algoritmo PEPS (Unificado)
        ListaIng & ListaSimples --> PEPS[Algoritmo PEPS: Buscar Lotes +Antigos]:::core
        
        PEPS --> CheckSaldo{Saldo Suficiente?}:::decision
        CheckSaldo -- Não --> Rollback[❌ Rollback Total: Erro Estoque]:::core
        CheckSaldo -- Sim --> Baixa[Gravar Movimentação SAÍDA]:::core
        
        Baixa --> ProxItem{Tem mais itens?}:::decision
        ProxItem -- Sim --> LoopItens
        ProxItem -- Não --> Commit[✅ Commit: Venda Finalizada]:::core
    end

    %% CONEXÕES ENTRE DOMÍNIOS
    DefFicha -.-> LerReceita
    CriaLote -.-> |Alimenta Estoque| PEPS
```

---

## 📖 Narrativa do Fluxo

### 1. Fundação & Catálogo (Fase Roxa)
Tudo começa com a autenticação e o **Tenant Manager**. O sistema isola os dados por empresa em cada query.
- Definimos os produtos como **Insumos** (ex: Carne Crua) ou **Compostos** (ex: X-Burger).
- Para produtos compostos, construímos a **Ficha Técnica** (BOM - Bill of Materials).

### 2. Supply Chain / Entrada (Fase Azul)
O estoque é abastecido principalmente pela importação de NFes.
- **Parser XML:** Valida e extrai dados da nota.
- **Lote & Validade:** Cada entrada gera ou atualiza lotes, essencial para o controle FEFO.
- **Recálculo de Custos:** Se o preço do insumo sobe na nota, o sistema recalcula automaticamente o custo teórico dos produtos compostos.

### 3. Operação de Frente (Fase Laranja)
A rotina operacional do restaurante.
- **Snapshot (Crítico):** Ao lançar um pedido, o sistema "fotografa" o custo e preço atuais. Isso protege a margem caso haja variações de preço durante o consumo da mesa.
- **KDS:** Roteamento para as telas de produção (Cozinha/Bar).

### 4. Processamento & Consolidação (Fase Verde)
O fechamento da venda dispara um processamento pesado para garantir integridade.
- **Explosão de Materiais:** Se vendeu um X-Burger, o sistema explode os ingredientes na hora da baixa.
- **Algoritmo FEFO (PEPS):** Busca os lotes mais antigos/perto do vencimento para realizar a baixa.
- **ACID Transaction:** Tudo (contas a receber e baixa de estoque) deve acontecer em uma única transação atômica. Se qualquer passo falhar (ex: falta de estoque real), ocorre um Rollback total.

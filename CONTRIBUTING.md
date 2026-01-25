# Contributing to Projeto Nix

Obrigado por considerar contribuir para o Projeto Nix! 🎉

## 📋 Código de Conduta

Este projeto adere ao [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Ao participar, você concorda em seguir este código.

## 🚀 Como Contribuir

### Reportar Bugs

1. Verifique se o bug já foi reportado em [Issues](https://github.com/seu-usuario/pedidos11/issues)
2. Se não, crie uma nova issue usando o template de bug
3. Inclua:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Screenshots (se aplicável)
   - Ambiente (OS, browser, versões)

### Sugerir Funcionalidades

1. Verifique se já não existe uma issue similar
2. Crie uma issue com o template de feature request
3. Descreva:
   - Problema que resolve
   - Solução proposta
   - Alternativas consideradas

### Pull Requests

1. **Fork o repositório**
2. **Clone seu fork:**
   ```bash
   git clone https://github.com/seu-usuario/pedidos11.git
   ```

3. **Crie uma branch:**
   ```bash
   git checkout -b feature/minha-feature
   # ou
   git checkout -b fix/meu-fix
   ```

4. **Faça suas alterações**

5. **Commit seguindo convenções:**
   ```bash
   git commit -m "feat: adiciona nova funcionalidade"
   # ou
   git commit -m "fix: corrige bug no carrinho"
   ```

6. **Push para seu fork:**
   ```bash
   git push origin feature/minha-feature
   ```

7. **Abra um Pull Request**

## 📝 Convenções de Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação (não afeta código)
- `refactor:` - Refatoração
- `test:` - Adicionar/modificar testes
- `chore:` - Manutenção

**Exemplos:**
```
feat: adiciona autenticação com JWT
fix: corrige cálculo de troco no PDV
docs: atualiza README com instruções de deploy
style: formata código com Prettier
refactor: reorganiza estrutura de pastas
test: adiciona testes para carrinho
chore: atualiza dependências
```

## 🏗️ Estrutura do Projeto

```
pedidos11/
├── backend/          # Django/DRF
│   ├── apps/        # Apps Django
│   └── config/      # Configurações
├── frontend/         # Next.js
│   ├── app/         # Pages (App Router)
│   └── src/         # Components, hooks, etc
└── docs/            # Documentação
```

## 🧪 Testes

### Backend (Django)

```bash
cd backend
pytest
pytest --cov=apps  # com cobertura
```

### Frontend (Next.js)

```bash
cd frontend
npm test
npm run test:coverage
```

### E2E

```bash
cd frontend
npx playwright test
```

## 📏 Padrões de Código

### Backend (Python)

- Follow PEP 8
- Use Black para formatação
- Use isort para imports
- Docstrings em funções complexas

```bash
black .
isort .
flake8
```

### Frontend (TypeScript)

- Use ESLint
- Use Prettier
- TypeScript strict mode
- Componentização clara

```bash
npm run lint
npm run format
npm run type-check
```

## 🔍 Code Review

Todos os PRs passam por code review. Procuramos:

- ✅ Código limpo e legível
- ✅ Testes adequados
- ✅ Documentação atualizada
- ✅ Sem breaking changes (ou documentados)
- ✅ Commits seguindo convenções

## 🎯 Prioridades

**High Priority:**
- Bugs críticos
- Security issues
- Performance problems

**Medium Priority:**
- Novas funcionalidades
- Melhorias de UX
- Refatorações

**Low Priority:**
- Documentação
- Testes adicionais
- Otimizações menores

## 💬 Comunicação

- **Issues:** Para bugs e features
- **Discussions:** Para perguntas e ideias
- **PR Comments:** Para feedback de código

## 📦 Versionamento

Usamos [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH`
- `1.0.0` - Release inicial
- `1.1.0` - Nova feature
- `1.1.1` - Bug fix

## ⚖️ Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

**Obrigado por contribuir! 🙏**

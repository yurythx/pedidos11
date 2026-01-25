# Instalar dependências do frontend que foram implementadas
Write-Host "🚀 Instalando dependências do Projeto Nix..." -ForegroundColor Cyan
Write-Host ""

# Navegar para frontend
Set-Location -Path "frontend"

Write-Host "📦 Instalando dependências principais..." -ForegroundColor Yellow
npm install

Write-Host ""
Write-Host "📦 Instalando dependências adicionais implementadas..." -ForegroundColor Yellow

# Dependências implementadas no projeto
npm install @tanstack/react-query
npm install zustand
npm install react-hook-form
npm install @hookform/resolvers/zod
npm install zod
npm install axios
npm install lucide-react

Write-Host ""
Write-Host "✅ Todas as dependências instaladas com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Configure o arquivo .env.local" -ForegroundColor White
Write-Host "   2. Execute: npm run dev" -ForegroundColor White
Write-Host ""

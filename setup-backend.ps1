# Setup completo do backend
Write-Host "🚀 Configurando Backend do Projeto Nix..." -ForegroundColor Cyan
Write-Host ""

# Navegar para backend
Set-Location -Path "backend"

Write-Host "🐍 Criando ambiente virtual..." -ForegroundColor Yellow
python -m venv venv

Write-Host ""
Write-Host "✅ Ambiente virtual criado!" -ForegroundColor Green

Write-Host ""
Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "🗄️ Executando migrações..." -ForegroundColor Yellow
python manage.py migrate

Write-Host ""
Write-Host "✅ Backend configurado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Crie um superusuário: python manage.py createsuperuser" -ForegroundColor White
Write-Host "   2. Configure o .env com SECRET_KEY" -ForegroundColor White
Write-Host "   3. Execute: python manage.py runserver" -ForegroundColor White
Write-Host ""

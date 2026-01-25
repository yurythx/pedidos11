#!/bin/bash
set -e

echo "🔄 Aguardando banco de dados..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✅ Banco de dados disponível!"

echo "🔄 Executando migrações..."
python manage.py migrate --noinput

echo "🔄 Criando superusuário padrão (se não existir)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuário criado: admin/admin123')
else:
    print('✅ Superusuário já existe')
EOF

echo "🚀 Iniciando servidor..."
exec "$@"

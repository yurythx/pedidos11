import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Cria/atualiza superusuário padrão a partir de variáveis de ambiente"

    def handle(self, *args, **options):
        username = os.getenv('DEFAULT_SUPERUSER_USERNAME', '').strip()
        password = os.getenv('DEFAULT_SUPERUSER_PASSWORD', '').strip()
        email = os.getenv('DEFAULT_SUPERUSER_EMAIL', '').strip()
        reset_pw = os.getenv('DEFAULT_SUPERUSER_RESET_PASSWORD', 'False').lower() in ('1','true','yes')
        if not username or not password:
            self.stdout.write(self.style.WARNING('DEFAULT_SUPERUSER_USERNAME/PASSWORD não definidos; nenhuma ação tomada'))
            return
        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user:
            changed = False
            if reset_pw:
                user.set_password(password)
                changed = True
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                changed = True
            if email and user.email != email:
                user.email = email
                changed = True
            if changed:
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Usuário {username} atualizado como superuser'))
            else:
                self.stdout.write(f'Usuário {username} já está configurado')
        else:
            User.objects.create_superuser(username=username, email=email or None, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superusuário {username} criado'))

from django.db import migrations


def add_clientes(apps, schema_editor):
    Account = apps.get_model('financeiro', 'Account')
    Account.objects.get_or_create(nome='Clientes', defaults={'codigo': '1200', 'tipo': 'ATIVO'})


def remove_clientes(apps, schema_editor):
    Account = apps.get_model('financeiro', 'Account')
    Account.objects.filter(nome='Clientes').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0003_seed_accounts'),
    ]
    operations = [
        migrations.RunPython(add_clientes, remove_clientes),
    ]

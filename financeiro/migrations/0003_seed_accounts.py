from django.db import migrations


def seed_accounts(apps, schema_editor):
    Account = apps.get_model('financeiro', 'Account')
    defaults = [
        ('Caixa', '1000', 'ATIVO'),
        ('Estoque', '1100', 'ATIVO'),
        ('Fornecedores', '2000', 'PASSIVO'),
        ('Receita de Vendas', '3000', 'RECEITA'),
        ('Custo das Vendas', '4000', 'DESPESA'),
    ]
    for nome, codigo, tipo in defaults:
        Account.objects.get_or_create(nome=nome, defaults={'codigo': codigo, 'tipo': tipo})


def unseed_accounts(apps, schema_editor):
    Account = apps.get_model('financeiro', 'Account')
    for nome in ['Caixa', 'Estoque', 'Fornecedores', 'Receita de Vendas', 'Custo das Vendas']:
        try:
            Account.objects.filter(nome=nome).delete()
        except Exception:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0002_ledgerentry_compra'),
    ]
    operations = [
        migrations.RunPython(seed_accounts, unseed_accounts),
    ]

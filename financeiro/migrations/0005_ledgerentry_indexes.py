from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0004_seed_clientes'),
    ]
    operations = [
        migrations.AddIndex(
            model_name='ledgerentry',
            index=models.Index(fields=['pedido'], name='le_pedido_idx'),
        ),
        migrations.AddIndex(
            model_name='ledgerentry',
            index=models.Index(fields=['compra'], name='le_compra_idx'),
        ),
        migrations.AddIndex(
            model_name='ledgerentry',
            index=models.Index(fields=['debit_account'], name='le_debit_idx'),
        ),
        migrations.AddIndex(
            model_name='ledgerentry',
            index=models.Index(fields=['credit_account'], name='le_credit_idx'),
        ),
        migrations.AddIndex(
            model_name='ledgerentry',
            index=models.Index(fields=['cost_center'], name='le_cc_idx'),
        ),
        migrations.AddIndex(
            model_name='ledgerentry',
            index=models.Index(fields=['criado_em'], name='le_criado_idx'),
        ),
    ]

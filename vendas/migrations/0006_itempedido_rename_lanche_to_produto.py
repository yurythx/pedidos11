from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0005_pedido_cost_center'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itempedido',
            old_name='lanche',
            new_name='produto',
        ),
    ]

from django.db import migrations, models
import decimal
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('vendas', '0011_produtoatributo_produtoatributovalor_produtovariacao'),
        ('compras', '0003_alter_purchaseorder_status'),
        ('financeiro', '0005_ledgerentry_indexes'),
    ]
    operations = [
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('AP', 'Contas a Pagar'), ('AR', 'Contas a Receber')], max_length=4)),
                ('descricao', models.CharField(blank=True, max_length=200)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=12)),
                ('valor_pago', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12)),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('Aberto', 'Aberto'), ('Quitado', 'Quitado'), ('Atrasado', 'Atrasado')], default='Aberto', max_length=20)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('pedido', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='titulos', to='vendas.pedido')),
                ('compra', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='titulos', to='compras.purchaseorder')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('cost_center', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='titulos', to='financeiro.costcenter')),
            ],
        ),
    ]

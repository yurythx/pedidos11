from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('estoque', '0001_initial'),
        ('vendas', '0007_alter_produto_categoria_alter_produto_imagem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StockReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fornecedor', models.CharField(blank=True, max_length=120)),
                ('documento', models.CharField(blank=True, max_length=64)),
                ('observacao', models.TextField(blank=True)),
                ('criado_em', models.DateTimeField()),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StockReceiptItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.IntegerField()),
                ('custo_unitario', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('criado_em', models.DateTimeField()),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vendas.produto')),
                ('recebimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='estoque.stockreceipt')),
            ],
        ),
    ]

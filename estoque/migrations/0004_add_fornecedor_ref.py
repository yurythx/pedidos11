from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('cadastro', '0001_initial'),
        ('estoque', '0003_alter_stockreceipt_criado_em_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockreceipt',
            name='fornecedor_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recebimentos', to='cadastro.supplier'),
        ),
    ]

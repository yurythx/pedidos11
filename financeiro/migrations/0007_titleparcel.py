from django.db import migrations, models
import decimal


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0006_title'),
    ]
    operations = [
        migrations.CreateModel(
            name='TitleParcel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=12)),
                ('valor_pago', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12)),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('Aberto', 'Aberto'), ('Quitado', 'Quitado'), ('Atrasado', 'Atrasado')], default='Aberto', max_length=20)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('title', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='parcelas', to='financeiro.title')),
            ],
        ),
    ]

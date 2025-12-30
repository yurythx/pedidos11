from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cadastro', '0002_customer'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='produto',
            table='cadastro_produto',
        ),
        migrations.AlterModelTable(
            name='produtoimagem',
            table='cadastro_produtoimagem',
        ),
        migrations.AlterModelTable(
            name='produtoatributo',
            table='cadastro_produtoatributo',
        ),
        migrations.AlterModelTable(
            name='produtoatributovalor',
            table='cadastro_produtoatributovalor',
        ),
        migrations.AlterModelTable(
            name='produtovariacao',
            table='cadastro_produtovariacao',
        ),
    ]

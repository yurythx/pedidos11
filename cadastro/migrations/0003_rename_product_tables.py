from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cadastro', '0002_customer'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL("ALTER TABLE vendas_produto RENAME TO cadastro_produto"),
                migrations.RunSQL("ALTER TABLE vendas_produtoimagem RENAME TO cadastro_produtoimagem"),
                migrations.RunSQL("ALTER TABLE vendas_produtoatributo RENAME TO cadastro_produtoatributo"),
                migrations.RunSQL("ALTER TABLE vendas_produtoatributovalor RENAME TO cadastro_produtoatributovalor"),
                migrations.RunSQL("ALTER TABLE vendas_produtovariacao RENAME TO cadastro_produtovariacao"),
            ],
            state_operations=[],
        ),
    ]

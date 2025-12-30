from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cadastro', '0003_rename_product_tables'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE vendas_categoria RENAME TO cadastro_categoria",
                    reverse_sql="ALTER TABLE cadastro_categoria RENAME TO vendas_categoria",
                ),
            ],
            state_operations=[],
        ),
    ]

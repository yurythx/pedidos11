from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cadastro', '0003_rename_product_tables'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='vendas_categoria') THEN
    EXECUTE 'ALTER TABLE vendas_categoria RENAME TO cadastro_categoria';
END IF;
END $$;
""",
                    reverse_sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='cadastro_categoria') THEN
    EXECUTE 'ALTER TABLE cadastro_categoria RENAME TO vendas_categoria';
END IF;
END $$;
""",
                ),
            ],
            state_operations=[],
        ),
    ]

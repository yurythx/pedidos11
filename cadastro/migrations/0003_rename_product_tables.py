from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cadastro', '0002_customer'),
        ('vendas', '0011_produtoatributo_produtoatributovalor_produtovariacao'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='vendas_produto') THEN
    EXECUTE 'ALTER TABLE vendas_produto RENAME TO cadastro_produto';
END IF;
END $$;
""",
                    reverse_sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='cadastro_produto') THEN
    EXECUTE 'ALTER TABLE cadastro_produto RENAME TO vendas_produto';
END IF;
END $$;
""",
                ),
                migrations.RunSQL(
                    sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='vendas_produtoimagem') THEN
    EXECUTE 'ALTER TABLE vendas_produtoimagem RENAME TO cadastro_produtoimagem';
END IF;
END $$;
""",
                    reverse_sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='cadastro_produtoimagem') THEN
    EXECUTE 'ALTER TABLE cadastro_produtoimagem RENAME TO vendas_produtoimagem';
END IF;
END $$;
""",
                ),
                migrations.RunSQL(
                    sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='vendas_produtoatributo') THEN
    EXECUTE 'ALTER TABLE vendas_produtoatributo RENAME TO cadastro_produtoatributo';
END IF;
END $$;
""",
                    reverse_sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='cadastro_produtoatributo') THEN
    EXECUTE 'ALTER TABLE cadastro_produtoatributo RENAME TO vendas_produtoatributo';
END IF;
END $$;
""",
                ),
                migrations.RunSQL(
                    sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='vendas_produtoatributovalor') THEN
    EXECUTE 'ALTER TABLE vendas_produtoatributovalor RENAME TO cadastro_produtoatributovalor';
END IF;
END $$;
""",
                    reverse_sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='cadastro_produtoatributovalor') THEN
    EXECUTE 'ALTER TABLE cadastro_produtoatributovalor RENAME TO vendas_produtoatributovalor';
END IF;
END $$;
""",
                ),
                migrations.RunSQL(
                    sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='vendas_produtovariacao') THEN
    EXECUTE 'ALTER TABLE vendas_produtovariacao RENAME TO cadastro_produtovariacao';
END IF;
END $$;
""",
                    reverse_sql="""
DO $$
BEGIN
IF EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tablename='cadastro_produtovariacao') THEN
    EXECUTE 'ALTER TABLE cadastro_produtovariacao RENAME TO vendas_produtovariacao';
END IF;
END $$;
""",
                ),
            ],
            state_operations=[],
        ),
    ]

from django.db import migrations, models


def backfill_sku(apps, schema_editor):
    Produto = apps.get_model('vendas', 'Produto')
    from django.utils.text import slugify
    for p in Produto.objects.all().order_by('id'):
        if not p.sku:
            base = slugify(p.nome)[:40] or f"produto-{p.id}"
            code = base
            i = 1
            while Produto.objects.filter(sku=code).exclude(pk=p.pk).exists():
                code = f"{base}-{i}"
                i += 1
            p.sku = code
            p.save(update_fields=['sku'])


class Migration(migrations.Migration):
    dependencies = [
        ('vendas', '0008_produto_ean_produto_marca_produto_sku_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_sku, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='produto',
            name='sku',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]

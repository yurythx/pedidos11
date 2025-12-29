from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Address(models.Model):
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=50, blank=True)
    complemento = models.CharField(max_length=200, blank=True)
    bairro = models.CharField(max_length=120, blank=True)
    cidade = models.CharField(max_length=120)
    estado = models.CharField(max_length=50, blank=True)
    cep = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=100, default='Brasil')
    referencia = models.CharField(max_length=200, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.logradouro}, {self.numero or ''} - {self.cidade}"


class Supplier(models.Model):
    nome = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=50, blank=True)
    documento = models.CharField(max_length=32, blank=True)
    enderecos = models.ManyToManyField(Address, blank=True, related_name='fornecedores')
    criado_em = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nome)
            slug = base
            i = 1
            while Supplier.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Customer(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=50, blank=True)
    documento = models.CharField(max_length=32, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='clientes')
    enderecos = models.ManyToManyField(Address, blank=True, related_name='clientes')
    criado_em = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nome)
            slug = base
            i = 1
            while Customer.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

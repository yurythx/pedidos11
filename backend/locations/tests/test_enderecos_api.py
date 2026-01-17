from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tenant.models import Empresa
from authentication.models import TipoCargo
from partners.models import Cliente

User = get_user_model()


class EnderecosAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.empresa = Empresa.objects.create(
            nome_fantasia='Empresa Teste',
            razao_social='Empresa Teste LTDA',
            cnpj='11222333000181',
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            empresa=self.empresa,
            cargo=TipoCargo.ADMIN,
        )
        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Demo',
            cpf_cnpj='12345678901',
            email='cliente@demo.com',
        )
        self.client.force_authenticate(user=self.admin)

    def test_criar_endereco_cliente(self):
        payload = {
            'content_type': 'partners.cliente',
            'object_id': str(self.cliente.id),
            'tipo': 'ENTREGA',
            'cep': '01310-100',
            'logradouro': 'Av. Paulista',
            'numero': '1000',
            'bairro': 'Bela Vista',
            'cidade': 'São Paulo',
            'uf': 'SP',
        }
        res = self.client.post('/api/enderecos/', payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['cidade'], 'São Paulo')
        # list
        res_list = self.client.get('/api/enderecos/')
        self.assertEqual(res_list.status_code, 200)
        results = res_list.data['results'] if isinstance(res_list.data, dict) and 'results' in res_list.data else res_list.data
        self.assertTrue(len(results) >= 1)


from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tenant.models import Empresa
from authentication.models import TipoCargo
from io import BytesIO
from PIL import Image


User = get_user_model()


def make_image_bytes():
    img = Image.new('RGB', (10, 10), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


class UsersAPITest(TestCase):
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
        self.user = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='senha123',
            empresa=self.empresa,
            cargo=TipoCargo.VENDEDOR,
            first_name='User',
            last_name='One',
        )
        self.client.force_authenticate(user=self.admin)

    def test_list_usuarios_mesma_empresa(self):
        res = self.client.get('/api/usuarios/')
        self.assertEqual(res.status_code, 200)
        ids = [u['id'] for u in res.data['results']] if isinstance(res.data, dict) and 'results' in res.data else [u['id'] for u in res.data]
        self.assertIn(self.admin.id, ids)
        self.assertIn(self.user.id, ids)

    def test_me_get_and_patch(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/usuarios/me/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['username'], 'user1')
        patch = {'first_name': 'User', 'last_name': 'Updated'}
        res2 = self.client.patch('/api/usuarios/me/', patch)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.data['last_name'], 'Updated')

    def test_me_upload_foto(self):
        self.client.force_authenticate(user=self.user)
        img = make_image_bytes()
        img.name = 'avatar.png'
        res = self.client.patch('/api/usuarios/me/', {'foto_perfil': img}, format='multipart')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get('foto_perfil') is not None)


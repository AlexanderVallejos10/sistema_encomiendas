import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import User

from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Empleado, Encomienda


@pytest.mark.django_db
class TestApiEncomiendas:

    def setup_method(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@gmail.com',
            password='test12345'
        )

        self.empleado = Empleado.objects.create(
            codigo='EMP-TEST',
            nombres='Empleado',
            apellidos='Prueba',
            email='testuser@gmail.com',
            cargo='Operador',
            fecha_ingreso=timezone.now().date(),
            estado=1
        )

        self.cliente1 = Cliente.objects.create(
            tipo_doc='DNI',
            nro_doc='11111111',
            nombres='Juan',
            apellidos='Perez',
            telefono='999999999',
            email='juan@gmail.com',
            estado=1
        )

        self.cliente2 = Cliente.objects.create(
            tipo_doc='DNI',
            nro_doc='22222222',
            nombres='Maria',
            apellidos='Lopez',
            telefono='988888888',
            email='maria@gmail.com',
            estado=1
        )

        self.ruta = Ruta.objects.create(
            codigo='RUT-TEST',
            origen='Lima',
            destino='Trujillo',
            precio_base='80.00',
            dias_entrega=2,
            estado=1
        )

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

    def test_listar_encomiendas_con_token(self):
        response = self.client.get('/api/v1/encomiendas/')

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_sin_token_devuelve_401(self):
        client = APIClient()
        response = client.get('/api/v1/encomiendas/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_crear_encomienda(self):
        data = {
            'descripcion': 'Paquete de prueba',
            'peso_kg': '5.00',
            'remitente': self.cliente1.id,
            'destinatario': self.cliente2.id,
            'ruta': self.ruta.id,
            'fecha_entrega_est': '2026-06-10'
        }

        response = self.client.post(
            '/api/v1/encomiendas/',
            data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['estado'] == 'PE'
        assert response.data['codigo'].startswith('ENC-')

    def test_cambiar_estado(self):
        encomienda = Encomienda.objects.create(
            codigo='ENC-TEST-001',
            descripcion='Caja prueba',
            peso_kg='3.00',
            costo_envio='80.00',
            remitente=self.cliente1,
            destinatario=self.cliente2,
            ruta=self.ruta,
            empleado_registro=self.empleado,
            estado='PE',
            fecha_entrega_est='2026-06-10'
        )

        response = self.client.post(
            f'/api/v1/encomiendas/{encomienda.id}/cambiar_estado/',
            {
                'estado': 'TR',
                'observacion': 'Salida de almacén'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK

        encomienda.refresh_from_db()
        assert encomienda.estado == 'TR'
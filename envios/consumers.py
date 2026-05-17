import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from my_project.choices import EstadoEnvio
from .models import Encomienda


class EncomiendaConsumer(AsyncWebsocketConsumer):
    """
    WebSocket global:
    ws://localhost:8000/ws/encomiendas/
    """

    async def connect(self):
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = 'encomiendas_global'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        stats = await self.get_stats()

        await self.send(text_data=json.dumps({
            'tipo': 'conectado',
            'usuario': user.username,
            'stats': stats,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'tipo': 'error',
                'mensaje': 'JSON inválido',
            }))
            return

        tipo = data.get('tipo')

        if tipo == 'ping':
            await self.send(text_data=json.dumps({
                'tipo': 'pong'
            }))

        elif tipo == 'solicitar_stats':
            stats = await self.get_stats()

            await self.send(text_data=json.dumps({
                'tipo': 'stats',
                'stats': stats,
            }))

        elif tipo == 'suscribir_encomienda':
            encomienda_id = data.get('encomienda_id')

            if encomienda_id:
                await self.channel_layer.group_add(
                    f'encomienda_{encomienda_id}',
                    self.channel_name
                )

                await self.send(text_data=json.dumps({
                    'tipo': 'suscrito',
                    'encomienda_id': encomienda_id,
                }))

    async def encomienda_estado_cambio(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'estado_cambio',
            'encomienda_id': event.get('encomienda_id'),
            'codigo': event.get('codigo'),
            'estado_anterior': event.get('estado_anterior'),
            'estado_nuevo': event.get('estado_nuevo'),
            'empleado': event.get('empleado'),
            'timestamp': event.get('timestamp'),
        }))

    async def dashboard_actualizar(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'stats_actualizado',
            'stats': event['stats'],
        }))

    @database_sync_to_async
    def get_stats(self):
        hoy = timezone.now().date()

        return {
            'activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.filter(
                estado=EstadoEnvio.EN_TRANSITO
            ).count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(
                estado=EstadoEnvio.ENTREGADO,
                fecha_entrega_real=hoy
            ).count(),
        }


class EncomiendaDetalleConsumer(AsyncWebsocketConsumer):
    """
    WebSocket por encomienda:
    ws://localhost:8000/ws/encomiendas/4/
    """

    async def connect(self):
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.encomienda_id = self.scope['url_route']['kwargs']['pk']
        self.group_name = f'encomienda_{self.encomienda_id}'

        existe = await self.encomienda_existe(self.encomienda_id)

        if not existe:
            await self.close(code=4004)
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        encomienda = await self.get_encomienda(self.encomienda_id)

        await self.send(text_data=json.dumps({
            'tipo': 'estado_actual',
            'encomienda': encomienda,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'tipo': 'error',
                'mensaje': 'JSON inválido',
            }))
            return

        if data.get('tipo') == 'ping':
            await self.send(text_data=json.dumps({
                'tipo': 'pong'
            }))

    async def encomienda_estado_cambio(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'estado_cambio',
            'encomienda_id': event.get('encomienda_id'),
            'codigo': event.get('codigo'),
            'estado_anterior': event.get('estado_anterior'),
            'estado_nuevo': event.get('estado_nuevo'),
            'empleado': event.get('empleado'),
            'timestamp': event.get('timestamp'),
        }))

    @database_sync_to_async
    def encomienda_existe(self, pk):
        return Encomienda.objects.filter(pk=pk).exists()

    @database_sync_to_async
    def get_encomienda(self, pk):
        enc = Encomienda.objects.select_related(
            'remitente',
            'destinatario',
            'ruta',
            'empleado_registro'
        ).get(pk=pk)

        return {
            'id': enc.id,
            'codigo': enc.codigo,
            'descripcion': enc.descripcion,
            'estado': enc.estado,
            'estado_display': enc.get_estado_display(),
            'remitente': enc.remitente.nombre_completo,
            'destinatario': enc.destinatario.nombre_completo,
            'origen': enc.ruta.origen,
            'destino': enc.ruta.destino,
            'fecha_entrega_est': str(enc.fecha_entrega_est),
            'fecha_entrega_real': str(enc.fecha_entrega_real) if enc.fecha_entrega_real else None,
        }


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket dashboard:
    ws://localhost:8000/ws/dashboard/
    """

    async def connect(self):
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = 'dashboard'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        stats = await self.get_stats()

        await self.send(text_data=json.dumps({
            'tipo': 'stats_iniciales',
            'stats': stats,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'tipo': 'error',
                'mensaje': 'JSON inválido',
            }))
            return

        if data.get('tipo') == 'ping':
            await self.send(text_data=json.dumps({
                'tipo': 'pong',
            }))

        elif data.get('tipo') == 'solicitar_stats':
            stats = await self.get_stats()

            await self.send(text_data=json.dumps({
                'tipo': 'stats',
                'stats': stats,
            }))

    async def dashboard_actualizar(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'stats_actualizado',
            'stats': event['stats'],
        }))

    async def encomienda_estado_cambio(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'estado_cambio',
            'encomienda_id': event.get('encomienda_id'),
            'codigo': event.get('codigo'),
            'estado_anterior': event.get('estado_anterior'),
            'estado_nuevo': event.get('estado_nuevo'),
            'empleado': event.get('empleado'),
            'timestamp': event.get('timestamp'),
        }))

    @database_sync_to_async
    def get_stats(self):
        hoy = timezone.now().date()

        return {
            'activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.filter(
                estado=EstadoEnvio.EN_TRANSITO
            ).count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(
                estado=EstadoEnvio.ENTREGADO,
                fecha_entrega_real=hoy
            ).count(),
        }
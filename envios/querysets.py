from django.db import models
from my_project.choices import EstadoEnvio


class EncomiendaQuerySet(models.QuerySet):

    def pendientes(self):
        return self.filter(estado=EstadoEnvio.PENDIENTE)

    def activas(self):
        return self.exclude(estado=EstadoEnvio.ENTREGADO)

    def con_retraso(self):
        from django.utils import timezone
        return self.filter(
            fecha_entrega_est__lt=timezone.now().date()
        ).exclude(estado=EstadoEnvio.ENTREGADO)

    def por_ruta(self, ruta):
        return self.filter(ruta=ruta)

"""
class ClienteQuerySet(models.QuerySet):

    def activos(self):
        return self.filter(estado=1)  # ACTIVO

    def buscar(self, termino):
        return self.filter(
            models.Q(nombres__icontains=termino) |
            models.Q(apellidos__icontains=termino)
        )"""
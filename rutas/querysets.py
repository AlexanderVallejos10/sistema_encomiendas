from django.db import models

class RutaQuerySet(models.QuerySet):
    def activas(self):
        return self.filter(estado=1)

    def de_baja(self):
        return self.filter(estado=9)

    def por_origen(self, origen):
        return self.filter(origen__icontains=origen)

    def por_destino(self, destino):
        return self.filter(destino__icontains=destino)
from django.db import models

class ClienteQuerySet(models.QuerySet):

    def activos(self):
        return self.filter(estado=1)  # 1 = ACTIVO (según tu choices)

    def buscar(self, termino):
        return self.filter(
            models.Q(nombres__icontains=termino) |
            models.Q(apellidos__icontains=termino) |
            models.Q(email__icontains=termino)
        )
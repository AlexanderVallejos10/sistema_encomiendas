from django.db import models

# Create your models here.

class Encomienda(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField()
    peso_kg = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.codigo
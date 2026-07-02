from django.db import models
from django.contrib.auth.models import User



class Habito(models.Model):
    FRECUENCIAS = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIAS, default='diario')

    dias = models.CharField(max_length=100, blank=True)

    xp = models.IntegerField(default=10)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

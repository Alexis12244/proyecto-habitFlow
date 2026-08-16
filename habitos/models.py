from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Habito(models.Model):

    TIPOS = [
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True
    )

    categoria = models.CharField(
        max_length=50
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
        default='positivo'
    )

    dias = models.CharField(
        max_length=150
    )

    xp = models.IntegerField(
        default=10
    )

    activo = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateField(
        default=timezone.now
    )

    def __str__(self):
        return self.nombre


class CumplimientoHabito(models.Model):

    habito = models.ForeignKey(
        Habito,
        on_delete=models.CASCADE,
        related_name='cumplimientos'
    )

    fecha = models.DateField(
        default=timezone.now
    )

    completado = models.BooleanField(
        default=True
    )

    class Meta:
        unique_together = ('habito', 'fecha')
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.habito.nombre} - {self.fecha}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Meta(models.Model):

    ESTADOS = [
        ('progreso', 'En progreso'),
        ('cumplida', 'Cumplida'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField()
    fecha_inicio = models.DateField(default=timezone.now)
    xp_recompensa = models.PositiveIntegerField(default=100)
    fecha_fin = models.DateField(
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='progreso'
    )

    @property
    def porcentaje(self):

        total = self.submetas.count()

        if total == 0:
            return 0

        hechas = self.submetas.filter(
            completada=True
        ).count()

        return int((hechas / total) * 100)

    @property
    def terminada(self):
        return self.porcentaje == 100

    def actualizar_estado(self):

        if self.porcentaje == 100:

            self.estado = "cumplida"

            if self.fecha_fin is None:
                self.fecha_fin = timezone.now().date()

        else:

            self.estado = "progreso"
            self.fecha_fin = None

        self.save()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        ordering = ['-fecha_inicio']

class SubMeta(models.Model):

    meta = models.ForeignKey(
        Meta,
        on_delete=models.CASCADE,
        related_name='submetas'
    )

    nombre = models.CharField(max_length=120)
    xp = models.IntegerField(default=20)
    completada = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=1)
    fecha_completada = models.DateField(blank=True,null=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'SubMeta'
        verbose_name_plural = 'SubMetas'
        ordering = ['orden']


from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    xp = models.PositiveIntegerField(
        default=0
    )

    nivel = models.PositiveIntegerField(
        default=1
    )

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    @property
    def xp_nivel_actual(self):
        """
        XP acumulada dentro del nivel actual.
        Cada nivel requiere 100 XP.
        """
        return self.xp % 100

    @property
    def xp_para_siguiente_nivel(self):
        """
        XP restante para subir al siguiente nivel.
        """
        return 100 - self.xp_nivel_actual

    @property
    def porcentaje_nivel(self):
        """
        Porcentaje de progreso del nivel actual.
        """
        return self.xp_nivel_actual

    def actualizar_nivel(self):
        """
        Calcula el nivel correspondiente a la XP actual.
        """

        self.nivel = (self.xp // 100) + 1

        self.save(
            update_fields=['nivel']
        )
from django.db import transaction

from .models import Perfil


@transaction.atomic
def agregar_xp(usuario, cantidad):
    """
    Agrega XP al perfil del usuario
    y actualiza automáticamente su nivel.
    """

    if cantidad <= 0:
        return usuario.perfil

    perfil = usuario.perfil

    perfil.xp += cantidad

    perfil.nivel = (perfil.xp // 100) + 1

    perfil.save(
        update_fields=[
            'xp',
            'nivel'
        ]
    )

    return perfil


@transaction.atomic
def quitar_xp(usuario, cantidad):
    """
    Quita XP del perfil del usuario.
    Nunca permite que la XP sea negativa.
    """

    if cantidad <= 0:
        return usuario.perfil

    perfil = usuario.perfil

    perfil.xp = max(
        0,
        perfil.xp - cantidad
    )

    perfil.nivel = (perfil.xp // 100) + 1

    perfil.save(
        update_fields=[
            'xp',
            'nivel'
        ]
    )

    return perfil
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from habitos.models import Habito, CumplimientoHabito


@login_required
def inicio(request):

    hoy = timezone.now().date()

    # Nombre del día actual en español
    dias_semana = {
        0: 'Lunes',
        1: 'Martes',
        2: 'Miércoles',
        3: 'Jueves',
        4: 'Viernes',
        5: 'Sábado',
        6: 'Domingo',
    }

    dia_hoy = dias_semana[hoy.weekday()]

    # Hábitos activos del usuario
    todos_habitos = Habito.objects.filter(
        usuario=request.user,
        activo=True
    )

    # Solo hábitos programados para hoy
    habitos_hoy = []

    for habito in todos_habitos:

        dias = [
            dia.strip()
            for dia in habito.dias.split(',')
            if dia.strip()
        ]

        if dia_hoy in dias:

            habito.completado_hoy = CumplimientoHabito.objects.filter(
                habito=habito,
                fecha=hoy,
                completado=True
            ).exists()

            habitos_hoy.append(habito)

    # Estadísticas del día
    total_hoy = len(habitos_hoy)

    completados_hoy = sum(
        1 for habito in habitos_hoy
        if habito.completado_hoy
    )

    pendientes_hoy = total_hoy - completados_hoy

    if total_hoy > 0:
        progreso_hoy = int(
            (completados_hoy / total_hoy) * 100
        )
    else:
        progreso_hoy = 0

    # XP ganado hoy
    xp_hoy = sum(
        habito.xp
        for habito in habitos_hoy
        if habito.completado_hoy
    )

    context = {
        'habitos_hoy': habitos_hoy,
        'dia_hoy': dia_hoy,
        'total_hoy': total_hoy,
        'completados_hoy': completados_hoy,
        'pendientes_hoy': pendientes_hoy,
        'progreso_hoy': progreso_hoy,
        'xp_hoy': xp_hoy,
    }

    return render(
        request,
        'inicio/inicio.html',
        context
    )
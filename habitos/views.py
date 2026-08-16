from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from .models import Habito, CumplimientoHabito

from usuarios.services import agregar_xp, quitar_xp

from calendar import monthcalendar
from datetime import date
import calendar
from datetime import date



from .models import Habito, CumplimientoHabito


@login_required
def habitos(request):

    # ==========================================
    # CREAR HÁBITO
    # ==========================================

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        tipo = request.POST.get('tipo', 'positivo')
        xp = request.POST.get('xp', 10)

        categoria_select = request.POST.get(
            'categoria_select',
            ''
        ).strip()

        custom_category = request.POST.get(
            'custom_category',
            ''
        ).strip()

        dias_lista = request.POST.getlist('dias')

        # Categoría
        if categoria_select == 'custom':
            categoria = custom_category
        else:
            categoria = categoria_select

        if not categoria:
            categoria = 'General'

        # Días seleccionados
        dias = ','.join(dias_lista)

        Habito.objects.create(
            usuario=request.user,
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            tipo=tipo,
            dias=dias,
            xp=xp
        )

        return redirect('habitos')


    # ==========================================
    # FECHA Y DÍA ACTUAL
    # ==========================================

    hoy = timezone.localtime().date()

    dias_semana = [
        'Lunes',
        'Martes',
        'Miércoles',
        'Jueves',
        'Viernes',
        'Sábado',
        'Domingo'
    ]

    dia_hoy = dias_semana[hoy.weekday()]


    # ==========================================
    # TODOS LOS HÁBITOS DEL USUARIO
    # ==========================================

    habitos_usuario = Habito.objects.filter(
        usuario=request.user,
        activo=True
    )


    # ==========================================
    # COMPROBAR COMPLETADOS HOY
    # ==========================================

    for habito in habitos_usuario:

        habito.completado_hoy = CumplimientoHabito.objects.filter(
            habito=habito,
            fecha=hoy,
            completado=True
        ).exists()

        # ¿Este hábito corresponde a hoy?
        habito.es_hoy = dia_hoy in habito.dias


    # ==========================================
    # FILTRO
    # ==========================================

    filtro = request.GET.get('filtro', 'activos')


    # ==========================================
    # ACTIVOS
    # Solo hábitos de hoy NO completados
    # ==========================================

    if filtro == 'activos':

        habitos = [
            habito
            for habito in habitos_usuario
            if habito.es_hoy and not habito.completado_hoy
        ]


    # ==========================================
    # COMPLETADOS
    # Solo hábitos de hoy completados
    # ==========================================

    elif filtro == 'completados':

        habitos = [
            habito
            for habito in habitos_usuario
            if habito.es_hoy and habito.completado_hoy
        ]


    # ==========================================
    # TODOS
    # ==========================================

    elif filtro == 'todos':

        habitos = list(habitos_usuario)


    # Si llega un filtro desconocido
    else:

        filtro = 'activos'

        habitos = [
            habito
            for habito in habitos_usuario
            if habito.es_hoy and not habito.completado_hoy
        ]


    return render(
        request,
        'habitos/index.html',
        {
            'habitos': habitos,
            'filtro': filtro,
            'dia_hoy': dia_hoy,
        }
    )


@login_required
def completar_habito(request, id):

    habito = get_object_or_404(
        Habito,
        id=id,
        usuario=request.user,
        activo=True
    )

    hoy = timezone.localtime().date()

    dias_semana = [
        'Lunes',
        'Martes',
        'Miércoles',
        'Jueves',
        'Viernes',
        'Sábado',
        'Domingo'
    ]

    dia_hoy = dias_semana[hoy.weekday()]


    # ==========================================
    # VERIFICAR SI EL HÁBITO CORRESPONDE A HOY
    # ==========================================

    if dia_hoy not in habito.dias:
        return redirect('habitos')


    # ==========================================
    # OBTENER / CREAR CUMPLIMIENTO
    # ==========================================

    cumplimiento, creado = CumplimientoHabito.objects.get_or_create(
        habito=habito,
        fecha=hoy
    )


    # ==========================================
    # COMPLETAR
    # ==========================================

    if creado:

        cumplimiento.completado = True
        cumplimiento.save()

        agregar_xp(
            request.user,
            habito.xp
        )


    # ==========================================
    # YA EXISTÍA
    # ==========================================

    else:

        # Descompletar
        if cumplimiento.completado:

            cumplimiento.completado = False
            cumplimiento.save()

            quitar_xp(
                request.user,
                habito.xp
            )

        # Volver a completar
        else:

            cumplimiento.completado = True
            cumplimiento.save()

            agregar_xp(
                request.user,
                habito.xp
            )


    return redirect('habitos')


@login_required
def eliminar_habito(request, id):

    habito = get_object_or_404(
        Habito,
        id=id,
        usuario=request.user
    )

    habito.activo = False
    habito.save()

    return redirect('habitos')


@login_required
def editar_habito(request, id):

    habito = get_object_or_404(
        Habito,
        id=id,
        usuario=request.user
    )

    categorias_predefinidas = [
        'Salud',
        'Fitness',
        'Estudio',
        'Productividad',
        'Finanzas',
        'Mindfulness',
        'Lectura'
    ]

    if request.method == 'POST':

        habito.nombre = request.POST.get('nombre')

        habito.descripcion = request.POST.get(
            'descripcion',
            ''
        )

        habito.tipo = request.POST.get(
            'tipo',
            'positivo'
        )

        habito.xp = request.POST.get(
            'xp',
            10
        )

        # Categoría
        categoria_select = request.POST.get(
            'categoria_select',
            ''
        ).strip()

        custom_category = request.POST.get(
            'custom_category',
            ''
        ).strip()

        if categoria_select == 'custom':
            habito.categoria = custom_category
        else:
            habito.categoria = categoria_select

        if not habito.categoria:
            habito.categoria = 'General'

        # Días
        dias = request.POST.getlist('dias')

        habito.dias = ','.join(dias)

        habito.save()

        return redirect('habitos')

    es_personalizada = (
        habito.categoria not in categorias_predefinidas
    )

    return render(
        request,
        'habitos/editar.html',
        {
            'habito': habito,
            'es_personalizada': es_personalizada
        }
    )


@login_required
def calendario_habitos(request):

    hoy = timezone.now().date()

    # Mes recibido desde la URL
    try:
        año = int(request.GET.get('año', hoy.year))
        mes = int(request.GET.get('mes', hoy.month))
    except (ValueError, TypeError):
        año = hoy.year
        mes = hoy.month

    # Si mes < 1 o > 12, corregimos
    if mes < 1:
        mes = 12
        año -= 1

    if mes > 12:
        mes = 1
        año += 1

    # Calendario comenzando en lunes
    cal = calendar.Calendar(firstweekday=0)
    semanas = cal.monthdayscalendar(año, mes)

    # Hábitos activos del usuario
    habitos_usuario = Habito.objects.filter(
        usuario=request.user,
        activo=True
    )

    # Cumplimientos del mes
    cumplimientos = CumplimientoHabito.objects.filter(
        habito__usuario=request.user,
        habito__activo=True,
        fecha__year=año,
        fecha__month=mes
    ).select_related('habito')

    # Fecha -> hábitos completados
    completados_por_fecha = {}

    for cumplimiento in cumplimientos:

        if not cumplimiento.completado:
            continue

        fecha = cumplimiento.fecha

        if fecha not in completados_por_fecha:
            completados_por_fecha[fecha] = []

        completados_por_fecha[fecha].append(
            cumplimiento.habito.nombre
        )

    # Crear información para cada día
    calendario = []

    dias_español = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    for semana in semanas:

        semana_datos = []

        for dia in semana:

            if dia == 0:
                semana_datos.append(None)
                continue

            fecha = date(año, mes, dia)

            nombre_dia = dias_español[
                fecha.strftime('%A')
            ]

            habitos_del_dia = []

            for habito in habitos_usuario:

                dias_habito = [
                    d.strip()
                    for d in habito.dias.split(',')
                    if d.strip()
                ]

                if nombre_dia in dias_habito:

                    completado = (
                        fecha in completados_por_fecha
                        and habito.nombre
                        in completados_por_fecha[fecha]
                    )

                    habitos_del_dia.append({
                        'nombre': habito.nombre,
                        'completado': completado
                    })

            total = len(habitos_del_dia)

            completados = sum(
                1
                for habito in habitos_del_dia
                if habito['completado']
            )

            porcentaje = 0

            if total > 0:
                porcentaje = int(
                    (completados / total) * 100
                )

            semana_datos.append({
                'dia': dia,
                'fecha': fecha,
                'es_hoy': fecha == hoy,
                'habitos': habitos_del_dia,
                'total': total,
                'completados': completados,
                'porcentaje': porcentaje
            })

        calendario.append(semana_datos)

    meses = [
        '',
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Diciembre'
    ]

    # Mes anterior
    if mes == 1:
        mes_anterior = 12
        año_anterior = año - 1
    else:
        mes_anterior = mes - 1
        año_anterior = año

    # Mes siguiente
    if mes == 12:
        mes_siguiente = 1
        año_siguiente = año + 1
    else:
        mes_siguiente = mes + 1
        año_siguiente = año

    return render(
        request,
        'habitos/calendario.html',
        {
            'calendario': calendario,
            'mes': meses[mes],
            'año': año,

            'mes_anterior': mes_anterior,
            'año_anterior': año_anterior,

            'mes_siguiente': mes_siguiente,
            'año_siguiente': año_siguiente,

            'hoy': hoy
        }
    )

@login_required
def estadisticas(request):

    hoy = timezone.now().date()

    # ==========================================================
    # HÁBITOS ACTIVOS DEL USUARIO
    # ==========================================================

    habitos = Habito.objects.filter(
        usuario=request.user,
        activo=True
    )

    # ==========================================================
    # CONVERSIÓN DE DÍAS
    # ==========================================================

    dias_semana = {
        0: 'Lunes',
        1: 'Martes',
        2: 'Miércoles',
        3: 'Jueves',
        4: 'Viernes',
        5: 'Sábado',
        6: 'Domingo'
    }

    # ==========================================================
    # FUNCIÓN PARA SABER SI UN HÁBITO CORRESPONDE A UN DÍA
    # ==========================================================

    def habito_corresponde(habito, fecha):

        dia = dias_semana[fecha.weekday()]

        dias_habito = [
            d.strip()
            for d in habito.dias.split(',')
            if d.strip()
        ]

        return dia in dias_habito

    # ==========================================================
    # ESTADÍSTICAS DE LOS ÚLTIMOS 7 DÍAS
    # ==========================================================

    estadisticas_semana = []

    for i in range(6, -1, -1):

        fecha = hoy - timedelta(days=i)

        # Hábitos que deberían realizarse ese día
        habitos_programados = [
            habito
            for habito in habitos
            if habito_corresponde(habito, fecha)
        ]

        total_programados = len(habitos_programados)

        # Cumplimientos de ese día
        cumplimientos = CumplimientoHabito.objects.filter(
            habito__usuario=request.user,
            fecha=fecha,
            completado=True
        )

        completados = 0
        xp_dia = 0

        for cumplimiento in cumplimientos:

            if cumplimiento.habito in habitos_programados:

                completados += 1
                xp_dia += cumplimiento.habito.xp

        # Productividad del día
        if total_programados > 0:
            porcentaje = int(
                (completados / total_programados) * 100
            )
        else:
            porcentaje = 0

        estadisticas_semana.append({
            'fecha': fecha,
            'nombre_dia': dias_semana[fecha.weekday()],
            'fecha_corta': fecha.strftime('%d/%m'),
            'total': total_programados,
            'completados': completados,
            'porcentaje': porcentaje,
            'xp': xp_dia
        })

    # ==========================================================
    # PRODUCTIVIDAD SEMANAL
    # ==========================================================

    dias_con_habitos = [
        dia
        for dia in estadisticas_semana
        if dia['total'] > 0
    ]

    if dias_con_habitos:

        productividad = int(
            sum(
                dia['porcentaje']
                for dia in dias_con_habitos
            )
            / len(dias_con_habitos)
        )

    else:

        productividad = 0

    # ==========================================================
    # MEJOR DÍA
    # ==========================================================

    mejor_dia = None

    if dias_con_habitos:

        mejor_dia = max(
            dias_con_habitos,
            key=lambda dia: dia['porcentaje']
        )

    # ==========================================================
    # PEOR DÍA
    # ==========================================================

    peor_dia = None

    if dias_con_habitos:

        peor_dia = min(
            dias_con_habitos,
            key=lambda dia: dia['porcentaje']
        )

    # ==========================================================
    # HÁBITOS COMPLETADOS ESTA SEMANA
    # ==========================================================

    total_completados_semana = sum(
        dia['completados']
        for dia in estadisticas_semana
    )

    # ==========================================================
    # XP GANADO ESTA SEMANA
    # ==========================================================

    xp_semana = sum(
        dia['xp']
        for dia in estadisticas_semana
    )

    # ==========================================================
    # Racha ACTUAL
    #
    # Un día cuenta para la racha si:
    # - tenía hábitos programados
    # - se completaron todos
    #
    # Si hoy todavía no tiene hábitos pendientes/completados,
    # revisamos desde ayer.
    # ==========================================================

    racha = 0

    fecha_revision = hoy

    while True:

        habitos_del_dia = [
            habito
            for habito in habitos
            if habito_corresponde(
                habito,
                fecha_revision
            )
        ]

        # Si no hay hábitos programados ese día,
        # simplemente continuamos buscando hacia atrás.
        if not habitos_del_dia:

            fecha_revision -= timedelta(days=1)

            # Evitamos buscar indefinidamente
            if racha == 0 and (
                hoy - fecha_revision
            ).days > 30:

                break

            continue

        completados_dia = CumplimientoHabito.objects.filter(
            habito__in=habitos_del_dia,
            fecha=fecha_revision,
            completado=True
        ).count()

        if completados_dia == len(habitos_del_dia):

            racha += 1
            fecha_revision -= timedelta(days=1)

        else:

            break

        # Seguridad
        if racha >= 3650:
            break

    # ==========================================================
    # HÁBITO MÁS CONSTANTE
    # ==========================================================

    habito_top = None
    habito_top_completados = 0

    for habito in habitos:

        cantidad = CumplimientoHabito.objects.filter(
            habito=habito,
            completado=True
        ).count()

        if cantidad > habito_top_completados:

            habito_top = habito
            habito_top_completados = cantidad

    # ==========================================================
    # POSITIVOS Y NEGATIVOS
    # ==========================================================

    positivos = habitos.filter(
        tipo='positivo'
    ).count()

    negativos = habitos.filter(
        tipo='negativo'
    ).count()

    # ==========================================================
    # ESTADÍSTICAS DE LOS ÚLTIMOS 30 DÍAS
    # ==========================================================

    estadisticas_mes = []

    for i in range(29, -1, -1):

        fecha = hoy - timedelta(days=i)

        habitos_programados = [
            habito
            for habito in habitos
            if habito_corresponde(habito, fecha)
        ]

        total_programados = len(
            habitos_programados
        )

        completados = CumplimientoHabito.objects.filter(
            habito__in=habitos_programados,
            fecha=fecha,
            completado=True
        ).count()

        if total_programados > 0:

            porcentaje = int(
                (completados / total_programados) * 100
            )

        else:

            porcentaje = 0

        estadisticas_mes.append({
            'fecha': fecha,
            'fecha_corta': fecha.strftime('%d/%m'),
            'porcentaje': porcentaje,
            'total': total_programados,
            'completados': completados
        })

    # ==========================================================
    # RENDER
    # ==========================================================

    return render(
        request,
        'habitos/estadisticas.html',
        {
            'estadisticas_semana': estadisticas_semana,
            'estadisticas_mes': estadisticas_mes,

            'productividad': productividad,

            'racha': racha,

            'mejor_dia': mejor_dia,
            'peor_dia': peor_dia,

            'total_completados_semana':
                total_completados_semana,

            'xp_semana': xp_semana,

            'habito_top': habito_top,
            'habito_top_completados':
                habito_top_completados,

            'positivos': positivos,
            'negativos': negativos,

            'total_habitos': habitos.count(),
        }
    )
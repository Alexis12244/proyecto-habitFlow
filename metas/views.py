from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse

from .models import Meta, SubMeta

from usuarios.services import agregar_xp, quitar_xp


@login_required
def metas(request):

    if request.method == 'POST':

        meta = Meta.objects.create(
            usuario=request.user,
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion'),
            fecha_inicio=request.POST.get('fecha_inicio'),
        )

        submetas = request.POST.getlist('submetas')

        for i, nombre in enumerate(submetas, start=1):

            nombre = nombre.strip()

            if nombre:

                SubMeta.objects.create(
                    meta=meta,
                    nombre=nombre,
                    orden=i
                )

        return redirect('metas')

    metas_usuario = Meta.objects.filter(
        usuario=request.user
    )

    total = metas_usuario.count()

    completadas = metas_usuario.filter(
        estado='cumplida'
    ).count()

    submetas_total = sum(
        meta.submetas.count()
        for meta in metas_usuario
    )

    progreso_general = 0

    if total > 0:

        progreso_general = int(
            sum(
                meta.porcentaje
                for meta in metas_usuario
            ) / total
        )

    return render(
        request,
        'metas/index.html',
        {
            'metas': metas_usuario,
            'total': total,
            'completadas': completadas,
            'submetas_total': submetas_total,
            'progreso_general': progreso_general,
        }
    )


@login_required
def completar_submeta(request, id):
    submeta = get_object_or_404(
        SubMeta,
        id=id,
        meta__usuario=request.user
    )

    # ==========================================
    # COMPLETAR / DESCOMPLETAR SUBMETA
    # ==========================================
    if not submeta.completada:
        submeta.completada = True
        submeta.fecha_completada = timezone.now().date()
        submeta.save()
        agregar_xp(request.user, submeta.xp)
    else:
        submeta.completada = False
        submeta.fecha_completada = None
        submeta.save()
        quitar_xp(request.user, submeta.xp)

    # ==========================================
    # ACTUALIZAR META DE LA SUBMETA
    # ==========================================
    meta = submeta.meta
    estado_anterior = meta.estado
    meta.actualizar_estado()
    estado_nuevo = meta.estado

    if estado_anterior != 'cumplida' and estado_nuevo == 'cumplida':
        agregar_xp(request.user, meta.xp_recompensa)
    elif estado_anterior == 'cumplida' and estado_nuevo != 'cumplida':
        quitar_xp(request.user, meta.xp_recompensa)

    # Refrescar perfil para la XP / Nivel
    perfil = request.user.perfil
    perfil.refresh_from_db()

    # ==========================================
    # RECALCULAR ESTADÍSTICAS GENERALES
    # ==========================================
    metas_usuario = Meta.objects.filter(usuario=request.user)
    total_metas = metas_usuario.count()
    completadas = metas_usuario.filter(estado='cumplida').count()
    
    progreso_general = 0
    if total_metas > 0:
        progreso_general = int(
            sum(m.porcentaje for m in metas_usuario) / total_metas
        )

    return JsonResponse({
        'completada': submeta.completada,
        'porcentaje': meta.porcentaje,
        'estado': meta.estado,
        'fecha_fin': (
            meta.fecha_fin.strftime('%d/%m/%Y')
            if meta.fecha_fin
            else None
        ),
        'perfil': {
            'nivel': perfil.nivel,
            'xp_actual': perfil.xp_nivel_actual,
            'porcentaje': perfil.porcentaje_nivel
        },
        # --- NUEVOS DATOS DE ESTADÍSTICAS ---
        'estadisticas': {
            'completadas': completadas,
            'progreso_general': progreso_general
        }
    })

@login_required
def editar_meta(request, id):

    meta = get_object_or_404(
        Meta,
        id=id,
        usuario=request.user
    )

    if request.method == 'POST':

        # ==========================
        # DATOS DE LA META
        # ==========================

        meta.nombre = request.POST.get(
            'nombre'
        )

        meta.descripcion = request.POST.get(
            'descripcion'
        )

        meta.fecha_inicio = request.POST.get(
            'fecha_inicio'
        )

        meta.save()

        # ==========================
        # SUBMETAS EXISTENTES
        # ==========================

        ids_submetas = request.POST.getlist(
            'submeta_id'
        )

        nombres_submetas = request.POST.getlist(
            'submeta_nombre'
        )

        descripciones_submetas = request.POST.getlist(
            'submeta_descripcion'
        )

        for i, submeta_id in enumerate(ids_submetas):

            submeta = get_object_or_404(
                SubMeta,
                id=submeta_id,
                meta=meta
            )

            if i < len(nombres_submetas):

                nombre = (
                    nombres_submetas[i].strip()
                )

            else:

                nombre = submeta.nombre

            if i < len(descripciones_submetas):

                descripcion = (
                    descripciones_submetas[i].strip()
                )

            else:

                descripcion = submeta.descripcion

            submeta.nombre = nombre
            submeta.descripcion = descripcion

            submeta.save()

        # ==========================
        # NUEVAS SUBMETAS
        # ==========================

        nuevas_submetas = request.POST.getlist(
            'nueva_submeta'
        )

        ultimo_orden = meta.submetas.count()

        for nombre in nuevas_submetas:

            nombre = nombre.strip()

            if nombre:

                ultimo_orden += 1

                SubMeta.objects.create(
                    meta=meta,
                    nombre=nombre,
                    orden=ultimo_orden
                )

        return redirect(
            'metas'
        )

    return render(
        request,
        'metas/editar.html',
        {
            'meta': meta
        }
    )


@login_required
def eliminar_submeta(request, id):

    submeta = get_object_or_404(
        SubMeta,
        id=id,
        meta__usuario=request.user
    )

    meta = submeta.meta

    # Si estaba completada, quitar su XP
    if submeta.completada:

        quitar_xp(
            request.user,
            submeta.xp
        )

    submeta.delete()

    # Guardar estado anterior
    estado_anterior = meta.estado

    # Recalcular estado
    meta.actualizar_estado()

    # Si la eliminación hizo que la meta
    # dejara de estar cumplida, quitar recompensa
    if (
        estado_anterior == 'cumplida'
        and meta.estado != 'cumplida'
    ):

        quitar_xp(
            request.user,
            meta.xp_recompensa
        )

    return redirect(
        'editar_meta',
        id=meta.id
    )


@login_required
def eliminar_meta(request, id):

    meta = get_object_or_404(
        Meta,
        id=id,
        usuario=request.user
    )

    if request.method == 'POST':

        # =====================================
        # REVERTIR XP DE SUBMETAS
        # =====================================

        for submeta in meta.submetas.all():

            if submeta.completada:

                quitar_xp(
                    request.user,
                    submeta.xp
                )

        # =====================================
        # REVERTIR XP DE META
        # =====================================

        if meta.estado == 'cumplida':

            quitar_xp(
                request.user,
                meta.xp_recompensa
            )

        meta.delete()

        return redirect(
            'metas'
        )

    return render(
        request,
        'metas/eliminar.html',
        {
            'meta': meta
        }
    )
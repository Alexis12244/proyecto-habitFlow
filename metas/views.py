from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Meta, SubMeta


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

    metas_usuario = Meta.objects.filter(usuario=request.user)

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
            sum(meta.porcentaje for meta in metas_usuario) / total
        )

    return render(request, 'metas/index.html', {
        'metas': metas_usuario,
        'total': total,
        'completadas': completadas,
        'submetas_total': submetas_total,
        'progreso_general': progreso_general,
    })
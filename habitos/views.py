from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Habito
from django.shortcuts import get_object_or_404


@login_required
def habitos(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        frecuencia = request.POST.get('frecuencia')

        categoria_select = request.POST.get('categoria_select', '').strip()
        custom_category = request.POST.get('custom_category', '').strip()

        dias = request.POST.getlist('dias')
        dias_string = ",".join(dias)

        if categoria_select == 'custom':
            categoria = custom_category
        else:
            categoria = categoria_select

        if not categoria:
            categoria = "General"

        Habito.objects.create(
            usuario=request.user,
            nombre=nombre,
            categoria=categoria,
            frecuencia=frecuencia,
            dias=dias_string
        )

        return redirect('habitos')

    habitos_usuario = Habito.objects.filter(
        usuario=request.user,
        activo=True
    )

    return render(
        request,
        'habitos/index.html',
        {'habitos': habitos_usuario}
    )

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

    if request.method == 'POST':
        habito.nombre = request.POST.get('nombre')
        habito.frecuencia = request.POST.get('frecuencia')

        categoria_select = request.POST.get('categoria_select', '').strip()
        custom_category = request.POST.get('custom_category', '').strip()

        if categoria_select == 'custom':
            habito.categoria = custom_category
        else:
            habito.categoria = categoria_select

        dias = request.POST.getlist('dias')
        habito.dias = ",".join(dias)

        habito.save()
        return redirect('habitos')

    return render(
        request,
        'habitos/editar.html',
        {'habito': habito}
    )


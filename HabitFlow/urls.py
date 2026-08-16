from django.contrib import admin
from django.urls import path

from habitos.views import (
    habitos,
    editar_habito,
    eliminar_habito,
    completar_habito,
    calendario_habitos,
    estadisticas
)

from inicio.views import inicio

from usuarios import views

from metas.views import (
    metas,
    completar_submeta,
    editar_meta,
    eliminar_submeta,
    eliminar_meta
)


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    # =========================
    # USUARIOS
    # =========================

    path(
        '',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),


    # =========================
    # INICIO
    # =========================

    path(
        'inicio/',
        inicio,
        name='inicio'
    ),


    # =========================
    # HÁBITOS
    # =========================

    path(
        'habitos/',
        habitos,
        name='habitos'
    ),

    path(
        'habitos/editar/<int:id>/',
        editar_habito,
        name='editar_habito'
    ),

    path(
        'habitos/eliminar/<int:id>/',
        eliminar_habito,
        name='eliminar_habito'
    ),

    path(
        'habitos/completar/<int:id>/',
        completar_habito,
        name='completar_habito'
    ),

    path(
        'habitos/calendario/',
        calendario_habitos,
        name='calendario_habitos'
    ),

    path(
        'habitos/estadisticas/',
        estadisticas,
        name='estadisticas'
    ),

    # =========================
    # METAS
    # =========================

    path(
        'metas/',
        metas,
        name='metas'
    ),

    path(
        'metas/completar_submeta/<int:id>/',
        completar_submeta,
        name='completar_submeta'
    ),

    path(
        'metas/editar/<int:id>/',
        editar_meta,
        name='editar_meta'
    ),

    path(
        'metas/eliminar_submeta/<int:id>/',
        eliminar_submeta,
        name='eliminar_submeta'
    ),

    path(
        'metas/eliminar_meta/<int:id>/',
        eliminar_meta,
        name='eliminar_meta'
    ),

]
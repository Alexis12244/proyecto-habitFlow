from django.contrib import admin
from django.urls import path, include
from django.contrib import admin
from django.urls import path
from habitos.views import habitos
from inicio.views import inicio
from usuarios import views
from habitos.views import habitos, editar_habito, eliminar_habito
from metas.views import metas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inicio/', inicio, name='inicio'),
    path('habitos/', habitos, name='habitos'),
    path('habitos/editar/<int:id>/', editar_habito, name='editar_habito'),
    path('habitos/eliminar/<int:id>/', eliminar_habito, name='eliminar_habito'),
    path('metas/', metas, name='metas'),
]

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User


def login_view(request):
    active_form = 'login'

    if request.method == 'POST':
        action = request.POST.get('action')

        # =========================
        # LOGIN
        # =========================
        if action == 'login':
            active_form = 'login'

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user:
                login(request, user)
                return redirect('inicio')
            else:
                messages.error(
                    request,
                    'Usuario o contraseña incorrectos'
                )

        # =========================
        # REGISTER
        # =========================
        elif action == 'register':
            active_form = 'register'

            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(
                    request,
                    'Las contraseñas no coinciden'
                )
            elif User.objects.filter(username=username).exists():
                messages.error(
                    request,
                    'Ese usuario ya existe'
                )
            else:
                User.objects.create_user(
                    username=username,
                    password=password
                )

                messages.success(
                    request,
                    'Cuenta creada correctamente. Ya puedes iniciar sesión.'
                )

                active_form = 'login'

    return render(
        request,
        'usuarios/login.html',
        {'active_form': active_form}
    )


def logout_view(request):
    logout(request)
    return redirect('login')

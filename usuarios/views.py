from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


def login_view(request):

    active_form = 'login'

    if request.method == 'POST':

        action = request.POST.get('action')


        # ==================================================
        # LOGIN
        # ==================================================

        if action == 'login':

            active_form = 'login'

            username = request.POST.get(
                'username',
                ''
            ).strip()

            password = request.POST.get(
                'password',
                ''
            )


            user = authenticate(
                request,
                username=username,
                password=password
            )


            if user is not None:

                login(
                    request,
                    user
                )

                return redirect('inicio')


            else:

                # No especificamos si falló usuario o contraseña.
                # Esto evita revelar qué usuarios existen.

                messages.error(
                    request,
                    'Usuario o contraseña incorrectos.'
                )


        # ==================================================
        # REGISTRO
        # ==================================================

        elif action == 'register':

            active_form = 'register'


            username = request.POST.get(
                'username',
                ''
            ).strip()

            password = request.POST.get(
                'password',
                ''
            )

            confirm_password = request.POST.get(
                'confirm_password',
                ''
            )


            # ==================================================
            # VALIDAR NOMBRE DE USUARIO
            # ==================================================

            if not username:

                messages.error(
                    request,
                    'Debes ingresar un nombre de usuario.'
                )


            # ==================================================
            # COMPROBAR SI EL USUARIO YA EXISTE
            # ==================================================

            elif User.objects.filter(
                username=username
            ).exists():

                messages.error(
                    request,
                    'Ese usuario ya existe.'
                )


            # ==================================================
            # COMPROBAR CONTRASEÑAS
            # ==================================================

            elif password != confirm_password:

                messages.error(
                    request,
                    'Las contraseñas no coinciden.'
                )


            # ==================================================
            # VALIDAR CONTRASEÑA
            # ==================================================

            else:

                try:

                    validate_password(
                        password,
                        user=User(
                            username=username
                        )
                    )


                except ValidationError as error:

                    # Django puede devolver varios errores
                    # al mismo tiempo.

                    for mensaje in error.messages:

                        messages.error(
                            request,
                            mensaje
                        )


                # ==================================================
                # CREAR USUARIO
                # ==================================================

                else:

                    User.objects.create_user(
                        username=username,
                        password=password
                    )


                    messages.success(
                        request,
                        'Cuenta creada correctamente. Ya puedes iniciar sesión.'
                    )


                    # Después de registrarse mostramos
                    # nuevamente el formulario de login.

                    active_form = 'login'


    # ==================================================
    # RENDER
    # ==================================================

    return render(
        request,
        'usuarios/login.html',
        {
            'active_form': active_form
        }
    )


# ==================================================
# CERRAR SESIÓN
# ==================================================

def logout_view(request):

    logout(request)

    return redirect('login')
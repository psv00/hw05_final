# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'signup/', views.SignUp.as_view(), name='signup'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path('password_reset/',
         PasswordResetView.as_view(), name='password_reset'),

    # Сообщение об отправке ссылки для восстановления пароля
    path('password_reset/done/', PasswordResetDoneView.as_view(),
         name='password_reset_done'
         ),

    # Вход по ссылке для восстановления пароля
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'
         ),

    # Сообщение об успешном восстановлении пароля
    path('reset/done/',
         PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

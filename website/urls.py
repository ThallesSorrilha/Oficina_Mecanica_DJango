
from django.urls import path
from .views import IndexView, ContatoView, SobreView, SignUpView

from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("contato/", ContatoView.as_view(), name="contato"),
    path("sobre/", SobreView.as_view(), name="sobre"),

    # Autenticação
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(template_name="website/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="index"), name="logout"),
    path("mudar-senha/", PasswordChangeView.as_view(
        template_name="website/mudar_senha.html"), name="mudar_senha"),
]

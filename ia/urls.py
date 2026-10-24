from django.urls import path

from .views import (
    ConfiguracaoIAUpdateView,
    IAUsuarioListView,
    IAUsuarioPadraoView,
    IAUsuarioUpdateView,
    MeuConsumoView,
    RequisicaoIADetailView,
    RequisicaoIAListView,
)

app_name = "ia"

urlpatterns = [
    path("requisicoes/", RequisicaoIAListView.as_view(), name="requisicoes"),
    path(
        "requisicoes/<int:pk>/",
        RequisicaoIADetailView.as_view(),
        name="requisicao-detalhe",
    ),
    path("consumo/", MeuConsumoView.as_view(), name="consumo"),
    path("configuracao/", ConfiguracaoIAUpdateView.as_view(), name="configuracao"),
    path("usuarios/", IAUsuarioListView.as_view(), name="usuarios"),
    path(
        "usuarios/<int:usuario_id>/",
        IAUsuarioUpdateView.as_view(),
        name="usuario-editar",
    ),
    path(
        "usuarios/<int:usuario_id>/padrao/",
        IAUsuarioPadraoView.as_view(),
        name="usuario-padrao",
    ),
]

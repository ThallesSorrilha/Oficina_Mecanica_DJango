from django.contrib import admin
from django import forms

from .models import ConfiguracaoIA, ConfiguracaoIAUsuario, ConsumoIA, RequisicaoIA


@admin.register(ConfiguracaoIA)
class ConfiguracaoIAAdmin(admin.ModelAdmin):
    list_display = ("provedor", "modelo", "atualizado_em")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["api_key"].widget = forms.PasswordInput(render_value=True)
        return form

    def has_add_permission(self, request):
        return not ConfiguracaoIA.objects.filter(pk=1).exists()


@admin.register(ConfiguracaoIAUsuario)
class ConfiguracaoIAUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "ia_habilitada", "limite_mensal")


@admin.register(RequisicaoIA)
class RequisicaoIAAdmin(admin.ModelAdmin):
    list_display = (
        "criado_em",
        "usuario",
        "finalidade",
        "tentativa",
        "situacao",
        "tokens_total",
    )
    list_filter = ("situacao", "origem", "provedor")
    readonly_fields = [field.name for field in RequisicaoIA._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConsumoIA)
class ConsumoIAAdmin(admin.ModelAdmin):
    list_display = ("dono", "mes", "tokens_total", "custo_estimado", "requisicoes")
    readonly_fields = [field.name for field in ConsumoIA._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

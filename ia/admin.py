from django.contrib import admin
from django import forms

from .models import ConfiguracaoIA, ConfiguracaoIAUsuario


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

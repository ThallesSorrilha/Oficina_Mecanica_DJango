from django.contrib import admin

from .models import ConfiguracaoIA, ConfiguracaoIAUsuario


@admin.register(ConfiguracaoIA)
class ConfiguracaoIAAdmin(admin.ModelAdmin):
    list_display = ("provedor", "modelo", "atualizado_em")

    def has_add_permission(self, request):
        return not ConfiguracaoIA.objects.filter(pk=1).exists()


@admin.register(ConfiguracaoIAUsuario)
class ConfiguracaoIAUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "ia_habilitada", "limite_mensal")

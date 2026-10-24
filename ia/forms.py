from django import forms

from .models import ConfiguracaoIA, ConfiguracaoIAUsuario


class ConfiguracaoIAForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoIA
        fields = [
            "modo_acesso",
            "api_key",
            "projeto_gcp",
            "regiao",
            "provedor",
            "modelo",
            "temperatura",
            "max_tokens_saida",
            "nivel_raciocinio",
            "tentativas",
            "timeout_s",
            "limite_mensal_usuario",
            "aviso_percentual",
            "reserva_minima_tokens",
            "limite_mensal_sistema",
            "tamanho_maximo_mb",
            "pdf_max_paginas",
            "reter_requisicoes_dias",
            "preco_entrada_milhao",
            "preco_saida_milhao",
        ]
        widgets = {
            "api_key": forms.PasswordInput(render_value=True),
        }


class ConfiguracaoIAUsuarioForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoIAUsuario
        fields = ["ia_habilitada", "limite_mensal", "observacao"]
        widgets = {
            "observacao": forms.Textarea(attrs={"rows": 4}),
        }

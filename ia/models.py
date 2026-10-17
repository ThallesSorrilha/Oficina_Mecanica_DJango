from decimal import Decimal

from django.core.cache import cache
from django.db import models


class ConfiguracaoIA(models.Model):
    PROVEDOR_GEMINI = "gemini"
    PROVEDOR_FALSO = "falso"
    PROVEDORES = (
        (PROVEDOR_GEMINI, "Gemini"),
        (PROVEDOR_FALSO, "Falso"),
    )
    NIVEIS_RACIOCINIO = (
        ("", "Padrão do modelo"),
        ("low", "Baixo"),
        ("medium", "Médio"),
        ("high", "Alto"),
    )
    provedor = models.CharField(
        "provedor",
        max_length=20,
        choices=PROVEDORES,
        default=PROVEDOR_GEMINI,
        help_text="Provedor usado para gerar respostas.",
    )
    modelo = models.CharField(
        "modelo",
        max_length=100,
        default="gemini-3.5-flash-lite",
        help_text="Nome do modelo usado pelo provedor.",
    )
    temperatura = models.DecimalField(
        "temperatura",
        max_digits=4,
        decimal_places=2,
        default=Decimal("0"),
        help_text="Temperatura usada na geração.",
    )
    max_tokens_saida = models.PositiveIntegerField(
        "máximo de tokens de saída",
        default=8192,
        help_text="Limite máximo de tokens gerados na saída.",
    )
    nivel_raciocinio = models.CharField(
        "nível de raciocínio",
        max_length=10,
        choices=NIVEIS_RACIOCINIO,
        default="low",
        help_text=(
            "Os níveis valem do Gemini 3 em diante. Com um modelo 2.5, "
            "deixe este campo vazio."
        ),
    )
    tentativas = models.PositiveIntegerField(
        "tentativas",
        default=2,
        help_text="Número de tentativas permitidas em erros temporários.",
    )
    timeout_s = models.PositiveIntegerField(
        "tempo limite em segundos",
        default=60,
        help_text="Tempo limite de cada chamada ao provedor.",
    )
    limite_mensal_usuario = models.PositiveIntegerField(
        "limite mensal por usuário",
        default=100000,
        help_text="Limite mensal de tokens por usuário.",
    )
    aviso_percentual = models.PositiveIntegerField(
        "percentual de aviso",
        default=80,
        help_text="Percentual do limite em que o usuário deve ser avisado.",
    )
    reserva_minima_tokens = models.PositiveIntegerField(
        "reserva mínima de tokens",
        default=5000,
        help_text="Reserva mínima de tokens para permitir uma solicitação.",
    )
    limite_mensal_sistema = models.PositiveIntegerField(
        "limite mensal do sistema",
        default=20000000,
        help_text="Limite mensal global; zero desliga este limite.",
    )
    tamanho_maximo_mb = models.PositiveIntegerField(
        "tamanho máximo em MB",
        default=10,
        help_text="Tamanho máximo permitido para arquivos enviados.",
    )
    pdf_max_paginas = models.PositiveIntegerField(
        "máximo de páginas PDF",
        default=10,
        help_text="Número máximo de páginas de um PDF.",
    )
    reter_requisicoes_dias = models.PositiveIntegerField(
        "reter requisições por dias",
        default=60,
        help_text="Quantidade de dias para manter requisições registradas.",
    )
    preco_entrada_milhao = models.DecimalField(
        "preço de entrada por milhão",
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Preço em US$ por milhão de tokens de entrada.",
    )
    preco_saida_milhao = models.DecimalField(
        "preço de saída por milhão",
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Preço em US$ por milhão de tokens de saída.",
    )
    atualizado_em = models.DateTimeField(
        "atualizado em",
        auto_now=True,
        help_text="Data e hora da última atualização da configuração.",
    )

    class Meta:
        verbose_name = "configuração de IA"
        verbose_name_plural = "configurações de IA"

    @classmethod
    def obter(cls):
        chave = "ia:configuracao"
        configuracao = cache.get(chave)
        if configuracao is None:
            configuracao, _ = cls.objects.get_or_create(pk=1)
            cache.set(chave, configuracao, 30)
        return configuracao

    def save(self, *args, **kwargs):
        self.pk = 1
        cache.delete("ia:configuracao")
        return super().save(*args, **kwargs)


class ConfiguracaoIAUsuario(models.Model):
    usuario = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="configuracao_ia",
        verbose_name="usuário",
        help_text="Usuário dono desta configuração.",
    )
    ia_habilitada = models.BooleanField(
        "IA habilitada",
        default=True,
        help_text="Permite que o usuário utilize a IA.",
    )
    limite_mensal = models.PositiveIntegerField(
        "limite mensal",
        null=True,
        blank=True,
        help_text="Vazio usa o padrão; zero não permite tokens.",
    )
    observacao = models.TextField(
        "observação",
        blank=True,
        help_text="Observação administrativa sobre a configuração.",
    )

    class Meta:
        verbose_name = "configuração de IA do usuário"
        verbose_name_plural = "configurações de IA dos usuários"

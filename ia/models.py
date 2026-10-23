from decimal import Decimal

from django.core.cache import cache
from django.db import models
from django.core.exceptions import ValidationError


class ConfiguracaoIA(models.Model):
    MODO_API_KEY = "api_key"
    MODO_ENTERPRISE = "enterprise"
    MODOS_ACESSO = (
        (MODO_API_KEY, "API Key (Google AI Studio)"),
        (MODO_ENTERPRISE, "Enterprise (Vertex AI / Google Cloud)"),
    )
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
    modo_acesso = models.CharField(
        "modo de acesso",
        max_length=20,
        choices=MODOS_ACESSO,
        default=MODO_API_KEY,
        help_text="Modo usado para acessar o Gemini.",
    )
    api_key = models.CharField(
        "Chave da API",
        max_length=200,
        blank=True,
        help_text="Só é usada quando o modo de acesso for API Key. Gere em aistudio.google.com.",
    )
    projeto_gcp = models.CharField(
        "ID do projeto no Google Cloud",
        max_length=100,
        blank=True,
        help_text="Só é usado quando o modo de acesso for Enterprise.",
    )
    regiao = models.CharField(
        "região",
        max_length=50,
        default="global",
        help_text="Só é usada no modo Enterprise. Use global, salvo se o professor indicar outra.",
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

    def __str__(self):
        return f"Configuração de IA ({self.get_provedor_display()})"

    def __repr__(self):
        return (
            f"<ConfiguracaoIA pk={self.pk!r} provedor={self.provedor!r} "
            f"modelo={self.modelo!r}>"
        )

    def clean(self):
        super().clean()
        if self.provedor != self.PROVEDOR_GEMINI:
            return
        if self.modo_acesso == self.MODO_API_KEY and not self.api_key:
            raise ValidationError({
                "api_key": "Preencha a Chave da API na tela Configuração da IA, ou mude o modo de acesso para Enterprise."
            })
        if self.modo_acesso == self.MODO_ENTERPRISE and not self.projeto_gcp:
            raise ValidationError({
                "projeto_gcp": "Preencha o ID do projeto no Google Cloud na tela Configuração da IA."
            })

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

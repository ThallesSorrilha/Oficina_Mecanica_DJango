from decimal import Decimal

from django.core.cache import cache
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


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


class RequisicaoIA(models.Model):
    SITUACOES = (
        ("sucesso", "Sucesso"),
        ("resposta_invalida", "Resposta inválida"),
        ("erro_temporario", "Erro temporário"),
        ("erro_permanente", "Erro permanente"),
        ("tempo_esgotado", "Tempo esgotado"),
        ("bloqueada_cota", "Bloqueada por cota"),
        ("bloqueada_seguranca", "Bloqueada por segurança"),
        ("indisponivel", "Indisponível"),
        ("erro_configuracao", "Erro de configuração"),
    )
    ORIGENS = (
        ("site", "Site"),
        ("telegram", "Telegram"),
        ("comando", "Comando"),
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="usuário",
    )
    referencia_tipo = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="tipo da referência",
    )
    referencia_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="ID da referência",
    )
    referencia = GenericForeignKey("referencia_tipo", "referencia_id")
    origem = models.CharField(
        "origem",
        max_length=20,
        choices=ORIGENS,
        default="site",
    )
    finalidade = models.CharField("finalidade", max_length=100, db_index=True)
    provedor = models.CharField("provedor", max_length=20, blank=True)
    modelo = models.CharField("modelo", max_length=100, blank=True)
    versao_prompt = models.CharField("versão do prompt", max_length=100, blank=True)
    tentativa = models.PositiveSmallIntegerField("tentativa", default=1)
    situacao = models.CharField("situação", max_length=30, choices=SITUACOES)
    tokens_entrada = models.PositiveBigIntegerField("tokens de entrada", default=0)
    tokens_saida = models.PositiveBigIntegerField("tokens de saída", default=0)
    tokens_raciocinio = models.PositiveBigIntegerField("tokens de raciocínio", default=0)
    tokens_total = models.PositiveBigIntegerField("tokens totais", default=0)
    custo_estimado = models.DecimalField(
        "custo estimado",
        max_digits=14,
        decimal_places=8,
        default=Decimal("0"),
    )
    duracao_ms = models.PositiveBigIntegerField("duração em milissegundos", default=0)
    motivo_fim = models.CharField("motivo do fim", max_length=100, blank=True)
    arquivo_mime = models.CharField("MIME do arquivo", max_length=100, blank=True)
    arquivo_tamanho = models.PositiveBigIntegerField("tamanho do arquivo", default=0)
    arquivo_hash = models.CharField("hash do arquivo", max_length=64, blank=True)
    resposta = models.TextField("resposta", blank=True)
    erro = models.TextField("erro", blank=True)
    contexto_hash = models.CharField("hash do contexto", max_length=64, blank=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "requisição de IA"
        verbose_name_plural = "requisições de IA"
        indexes = [
            models.Index(fields=["usuario", "-criado_em"]),
            models.Index(fields=["situacao", "-criado_em"]),
            models.Index(fields=["referencia_tipo", "referencia_id", "-criado_em"]),
        ]


class ConsumoIA(models.Model):
    dono = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="consumos_ia",
        verbose_name="dono da cota",
    )
    mes = models.DateField("mês")
    tokens_entrada = models.PositiveBigIntegerField("tokens de entrada", default=0)
    tokens_saida = models.PositiveBigIntegerField("tokens de saída", default=0)
    tokens_total = models.PositiveBigIntegerField("tokens totais", default=0)
    custo_estimado = models.DecimalField(
        "custo estimado",
        max_digits=14,
        decimal_places=8,
        default=Decimal("0"),
    )
    requisicoes = models.PositiveIntegerField("requisições", default=0)

    class Meta:
        verbose_name = "consumo de IA"
        verbose_name_plural = "consumos de IA"
        constraints = [
            models.UniqueConstraint(fields=["dono", "mes"], name="ia_consumo_dono_mes"),
        ]

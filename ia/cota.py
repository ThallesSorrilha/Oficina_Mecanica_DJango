from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import F, Sum

from .models import ConfiguracaoIA, ConfiguracaoIAUsuario, ConsumoIA


FUSO_SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def mes_atual():
    hoje = datetime.now(FUSO_SAO_PAULO).date()
    return hoje.replace(day=1)


def proximo_mes(mes):
    if mes.month == 12:
        return mes.replace(year=mes.year + 1, month=1)
    return mes.replace(month=mes.month + 1)


def dono_da_cota(usuario):
    return usuario


def limite_do_usuario(usuario):
    configuracao = ConfiguracaoIA.obter()
    try:
        limite = ConfiguracaoIAUsuario.objects.get(usuario=usuario).limite_mensal
    except ConfiguracaoIAUsuario.DoesNotExist:
        limite = None
    return configuracao.limite_mensal_usuario if limite is None else limite


@dataclass(frozen=True)
class SituacaoCota:
    usado: int
    limite: int
    restante: int
    percentual: Decimal
    renova_em: date
    esgotada: bool
    em_alerta: bool

    def mensagem_esgotada(self):
        return f"Sua cota de IA acabou. Ela renova em {self.renova_em:%d/%m}."


class CotaExcedida(Exception):
    def __init__(self, situacao=None):
        super().__init__("A cota de IA foi excedida.")
        self.situacao = situacao


def _consumo(dono, mes=None):
    return ConsumoIA.objects.filter(dono=dono, mes=mes or mes_atual()).first()


def situacao_da_cota(dono):
    configuracao = ConfiguracaoIA.obter()
    limite = limite_do_usuario(dono)
    consumo = _consumo(dono)
    usado = consumo.tokens_total if consumo else 0
    restante = max(limite - usado, 0)
    percentual = (
        Decimal("0")
        if limite == 0
        else (Decimal(usado) * Decimal("100") / Decimal(limite))
    )
    return SituacaoCota(
        usado=usado,
        limite=limite,
        restante=restante,
        percentual=percentual,
        renova_em=proximo_mes(mes_atual()),
        esgotada=(
            limite == 0
            or restante <= 0
            or restante < configuracao.reserva_minima_tokens
        ),
        em_alerta=percentual >= configuracao.aviso_percentual,
    )


def verificar(dono):
    situacao = situacao_da_cota(dono)
    if situacao.esgotada:
        raise CotaExcedida(situacao)
    return situacao


def teto_do_sistema_atingido():
    configuracao = ConfiguracaoIA.obter()
    limite = configuracao.limite_mensal_sistema
    if limite == 0:
        return False
    usado = (
        ConsumoIA.objects.filter(mes=mes_atual()).aggregate(total=Sum("tokens_total"))[
            "total"
        ]
        or 0
    )
    return usado >= limite


def custo_estimado(uso):
    configuracao = ConfiguracaoIA.obter()
    preco_entrada = configuracao.preco_entrada_milhao or Decimal("0")
    preco_saida = configuracao.preco_saida_milhao or Decimal("0")
    return (
        Decimal(uso.entrada) * preco_entrada
        + Decimal(uso.saida) * preco_saida
    ) / Decimal("1000000")


def registrar_consumo(dono, uso, custo):
    mes = mes_atual()
    with transaction.atomic():
        consumo, _ = ConsumoIA.objects.get_or_create(dono=dono, mes=mes)
        ConsumoIA.objects.filter(pk=consumo.pk).update(
            tokens_entrada=F("tokens_entrada") + uso.entrada,
            tokens_saida=F("tokens_saida") + uso.saida,
            tokens_total=F("tokens_total") + uso.total,
            custo_estimado=F("custo_estimado") + custo,
            requisicoes=F("requisicoes") + 1,
        )
    return ConsumoIA.objects.get(pk=consumo.pk)

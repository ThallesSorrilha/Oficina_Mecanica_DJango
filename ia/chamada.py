import hashlib
import logging
import time

from django.contrib.contenttypes.models import ContentType
from .cota import (
    CotaExcedida,
    custo_estimado,
    dono_da_cota,
    registrar_consumo,
    teto_do_sistema_atingido,
    verificar,
)
from .models import ConfiguracaoIA, ConfiguracaoIAUsuario, RequisicaoIA
from .provedores import obter_provedor
from .provedores.base import (
    ErroIA,
    ErroTemporario,
    IaIndisponivel,
    PedidoIA,
    RespostaIA,
    UsoTokens,
)
from pydantic import BaseModel


logger = logging.getLogger(__name__)


def _referencia(referencia):
    if referencia is None:
        return None, None
    return (
        ContentType.objects.get_for_model(referencia),
        referencia.pk,
    )


def _auditar(**dados):
    try:
        RequisicaoIA.objects.create(**dados)
    except Exception:
        logger.exception("Falha ao gravar auditoria da requisição de IA.")


def _hash_contexto(pedido):
    texto = pedido.instrucoes + "\n" + pedido.texto
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _registro_base(usuario, finalidade, origem, referencia, versao_prompt, arquivo_info):
    tipo, identificador = _referencia(referencia)
    arquivo_info = arquivo_info or {}
    return {
        "usuario": usuario,
        "referencia_tipo": tipo,
        "referencia_id": identificador,
        "origem": origem,
        "finalidade": finalidade,
        "versao_prompt": versao_prompt,
        "arquivo_mime": arquivo_info.get("mime", ""),
        "arquivo_tamanho": arquivo_info.get("tamanho", 0),
        "arquivo_hash": arquivo_info.get("hash", ""),
    }


def chamar_ia(
    *,
    finalidade,
    montar_pedido,
    usuario,
    origem="site",
    referencia=None,
    versao_prompt="",
    arquivo_info=None,
):
    config = ConfiguracaoIA.obter()
    registro = _registro_base(
        usuario, finalidade, origem, referencia, versao_prompt, arquivo_info
    )
    usuario_config = ConfiguracaoIAUsuario.objects.filter(usuario=usuario).first()
    if usuario_config and not usuario_config.ia_habilitada:
        _auditar(**registro, provedor=config.provedor, modelo=config.modelo, situacao="indisponivel")
        raise IaIndisponivel("A IA está desabilitada para este usuário.")

    dono = dono_da_cota(usuario)
    if teto_do_sistema_atingido():
        _auditar(**registro, provedor=config.provedor, modelo=config.modelo, situacao="indisponivel")
        raise IaIndisponivel("O limite mensal do sistema foi atingido.")
    try:
        verificar(dono)
    except CotaExcedida as exc:
        _auditar(**registro, provedor=config.provedor, modelo=config.modelo, situacao="bloqueada_cota")
        raise

    pedido = montar_pedido(config)
    try:
        provedor = obter_provedor(config)
    except ErroIA as exc:
        _auditar(
            **registro,
            provedor=config.provedor,
            modelo=exc.modelo or config.modelo,
            situacao=exc.situacao,
            erro=str(exc),
            contexto_hash=_hash_contexto(pedido),
        )
        raise
    tentativas = max(config.tentativas, 1)
    for numero in range(1, tentativas + 1):
        inicio = time.monotonic()
        try:
            resposta = provedor.gerar(pedido)
        except ErroIA as exc:
            duracao = int((time.monotonic() - inicio) * 1000)
            uso = exc.uso or UsoTokens()
            custo = custo_estimado(uso)
            registro_erro = {
                **registro,
                "provedor": config.provedor,
                "modelo": exc.modelo or config.modelo,
                "tentativa": numero,
                "situacao": exc.situacao,
                "tokens_entrada": uso.entrada,
                "tokens_saida": uso.saida,
                "tokens_raciocinio": uso.raciocinio,
                "tokens_total": uso.total,
                "custo_estimado": custo,
                "duracao_ms": duracao,
                "motivo_fim": getattr(exc, "motivo_fim", ""),
                "resposta": (exc.texto_bruto or "")[:20000],
                "erro": str(exc),
                "contexto_hash": _hash_contexto(pedido),
            }
            _auditar(**registro_erro)
            if uso.total:
                registrar_consumo(dono, uso, custo)
            if isinstance(exc, ErroTemporario) and numero < tentativas:
                time.sleep(numero)
                continue
            raise
        except Exception as exc:
            erro = ErroIA(str(exc), modelo=config.modelo)
            erro.situacao = "indisponivel"
            erro.__traceback__ = exc.__traceback__
            raise erro from exc

        duracao = int((time.monotonic() - inicio) * 1000)
        uso = resposta.uso
        custo = custo_estimado(uso)
        _auditar(
            **registro,
            provedor=config.provedor,
            modelo=resposta.modelo,
            tentativa=numero,
            situacao="sucesso",
            tokens_entrada=uso.entrada,
            tokens_saida=uso.saida,
            tokens_raciocinio=uso.raciocinio,
            tokens_total=uso.total,
            custo_estimado=custo,
            duracao_ms=duracao,
            motivo_fim=resposta.motivo_fim,
            resposta=resposta.texto[:20000],
            contexto_hash=_hash_contexto(pedido),
        )
        if uso.total:
            registrar_consumo(dono, uso, custo)
        return resposta


def testar_conexao(usuario):
    class RespostaTeste(BaseModel):
        status: str

    def montar_pedido(config):
        return PedidoIA(
            instrucoes="Responda somente JSON.",
            texto='Responda {"status": "ok"}.',
            esquema=RespostaTeste,
        )

    resposta = chamar_ia(
        finalidade="teste_conexao",
        montar_pedido=montar_pedido,
        usuario=usuario,
    )
    config = ConfiguracaoIA.obter()
    if config.modo_acesso == config.MODO_API_KEY:
        modo = "API Key"
    else:
        modo = f"Enterprise ({config.projeto_gcp}, região {config.regiao})"
    return resposta, f"Conexão realizada usando {modo}."

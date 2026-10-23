import importlib
from threading import Lock

from .base import ErroConfiguracao, ProvedorIA


PROVEDORES = {
    "gemini": "ia.provedores.gemini.ProvedorGemini",
    "falso": "ia.provedores.falso.ProvedorFalso",
}

_provedores = {}
_lock = Lock()


def obter_provedor(config):
    try:
        caminho = PROVEDORES[config.provedor]
    except KeyError as exc:
        raise ErroConfiguracao(
            f"Provedor de IA desconhecido: {config.provedor}."
        ) from exc

    if config.provedor == "gemini":
        if config.modo_acesso == "api_key" and not config.api_key:
            raise ErroConfiguracao(
                "Preencha a Chave da API na tela Configuração da IA, ou mude o modo de acesso para Enterprise."
            )
        if config.modo_acesso == "enterprise" and not config.projeto_gcp:
            raise ErroConfiguracao(
                "Preencha o ID do projeto no Google Cloud na tela Configuração da IA."
            )

    cache_key = (config.provedor, config.atualizado_em)
    with _lock:
        provedor = _provedores.get(cache_key)
        if provedor is None:
            modulo_nome, classe_nome = caminho.rsplit(".", 1)
            classe = getattr(importlib.import_module(modulo_nome), classe_nome)
            provedor = classe(config=config)
            _provedores[cache_key] = provedor
        return provedor

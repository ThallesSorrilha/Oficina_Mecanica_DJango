import importlib
import os
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

    chave = os.getenv("GEMINI_API_KEY", "")
    if config.provedor == "gemini" and not chave:
        raise ErroConfiguracao(
            "GEMINI_API_KEY não foi definida no ambiente ou no arquivo .env."
        )

    cache_key = (config.provedor, config.atualizado_em)
    with _lock:
        provedor = _provedores.get(cache_key)
        if provedor is None:
            modulo_nome, classe_nome = caminho.rsplit(".", 1)
            classe = getattr(importlib.import_module(modulo_nome), classe_nome)
            provedor = classe(config=config, chave=chave)
            _provedores[cache_key] = provedor
        return provedor

from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class Arquivo:
    conteudo: bytes
    mime: str
    nome: str = ""


@dataclass(frozen=True)
class MensagemHistorico:
    papel: str
    texto: str


@dataclass(frozen=True)
class PedidoIA:
    instrucoes: str
    texto: str
    arquivos: tuple = ()
    historico: tuple = ()
    esquema: type[BaseModel] | None = None


@dataclass(frozen=True)
class UsoTokens:
    entrada: int = 0
    saida: int = 0
    raciocinio: int = 0

    @property
    def total(self):
        return self.entrada + self.saida


@dataclass(frozen=True)
class RespostaIA:
    texto: str
    dados: BaseModel | None
    uso: UsoTokens
    modelo: str
    motivo_fim: str
    id_resposta: str = ""


class ErroIA(Exception):
    situacao = "erro_ia"

    def __init__(
        self,
        mensagem="",
        *,
        uso=None,
        texto_bruto="",
        modelo="",
    ):
        super().__init__(mensagem)
        self.uso = uso or UsoTokens()
        self.texto_bruto = texto_bruto
        self.modelo = modelo


class ErroTemporario(ErroIA):
    situacao = "erro_temporario"


class TempoEsgotado(ErroTemporario):
    situacao = "tempo_esgotado"


class ErroPermanente(ErroIA):
    situacao = "erro_permanente"


class RespostaInvalida(ErroIA):
    situacao = "resposta_invalida"


class BloqueioSeguranca(ErroIA):
    situacao = "bloqueada_seguranca"


class ErroConfiguracao(ErroIA):
    situacao = "erro_configuracao"


class IaIndisponivel(ErroIA):
    situacao = "indisponivel"


class ProvedorIA(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def gerar(self, pedido: PedidoIA) -> RespostaIA:
        raise NotImplementedError

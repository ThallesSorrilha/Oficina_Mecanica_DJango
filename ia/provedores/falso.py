from collections import deque

from .base import PedidoIA, ProvedorIA, RespostaIA, UsoTokens


class ProvedorFalso(ProvedorIA):
    def __init__(self, config):
        super().__init__(config)
        self.pedidos = []
        self._respostas = deque()

    def programar(self, texto="", dados=None, uso=None, erro=None):
        self._respostas.append(
            {
                "texto": texto,
                "dados": dados,
                "uso": uso or UsoTokens(),
                "erro": erro,
            }
        )

    def gerar(self, pedido: PedidoIA) -> RespostaIA:
        self.pedidos.append(pedido)
        programada = (
            self._respostas.popleft()
            if self._respostas
            else {"texto": "ok", "dados": None, "uso": UsoTokens(), "erro": None}
        )
        if programada["erro"] is not None:
            raise programada["erro"]
        return RespostaIA(
            texto=programada["texto"],
            dados=programada["dados"],
            uso=programada["uso"],
            modelo=self.config.modelo,
            motivo_fim="STOP",
        )

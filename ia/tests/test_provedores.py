from unittest.mock import patch

from django.test import TestCase

from ia.models import ConfiguracaoIA
from ia.provedores import obter_provedor
from ia.provedores.base import ErroConfiguracao, ErroPermanente, PedidoIA
from ia.provedores.falso import ProvedorFalso


class ProvedoresTests(TestCase):
    def test_obter_cria_configuracao_unica_e_reutiliza_instancia(self):
        primeira = ConfiguracaoIA.obter()
        segunda = ConfiguracaoIA.obter()

        self.assertEqual(primeira.pk, 1)
        self.assertEqual(primeira.pk, segunda.pk)
        self.assertEqual(ConfiguracaoIA.objects.count(), 1)

    @patch.dict("os.environ", {"GEMINI_API_KEY": "chave-teste"})
    @patch("ia.provedores.gemini.genai.Client")
    def test_salvar_configuracao_cria_cliente_novo(self, cliente):
        configuracao = ConfiguracaoIA.objects.create(pk=1)
        primeiro = obter_provedor(configuracao)
        configuracao.modelo = "outro-modelo"
        configuracao.save()
        segundo = obter_provedor(configuracao)

        self.assertIsNot(primeiro, segundo)
        self.assertEqual(cliente.call_count, 2)

    def test_provedor_falso_entrega_fila_e_erro(self):
        configuracao = ConfiguracaoIA.objects.create(pk=1, provedor="falso")
        provedor = ProvedorFalso(configuracao, "")
        erro = ErroPermanente("erro programado")
        provedor.programar("primeira")
        provedor.programar("segunda")
        provedor.programar(erro=erro)

        self.assertEqual(provedor.gerar(PedidoIA("", "")).texto, "primeira")
        self.assertEqual(provedor.gerar(PedidoIA("", "")).texto, "segunda")
        with self.assertRaises(ErroPermanente):
            provedor.gerar(PedidoIA("", ""))
        self.assertEqual(len(provedor.pedidos), 3)

    def test_gemini_sem_chave_levanta_erro_configuracao(self):
        configuracao = ConfiguracaoIA.objects.create(pk=1)
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ErroConfiguracao):
                obter_provedor(configuracao)

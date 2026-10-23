from unittest.mock import patch

from django.core.exceptions import ValidationError
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

    @patch("ia.provedores.gemini.genai.Client")
    def test_salvar_configuracao_cria_cliente_novo(self, cliente):
        configuracao = ConfiguracaoIA.objects.create(pk=1, api_key="chave-teste")
        primeiro = obter_provedor(configuracao)
        configuracao.modelo = "outro-modelo"
        configuracao.save()
        segundo = obter_provedor(configuracao)

        self.assertIsNot(primeiro, segundo)
        self.assertEqual(cliente.call_count, 2)

    def test_provedor_falso_entrega_fila_e_erro(self):
        configuracao = ConfiguracaoIA.objects.create(pk=1, provedor="falso")
        provedor = ProvedorFalso(configuracao)
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
        with self.assertRaisesMessage(
            ErroConfiguracao,
            "Preencha a Chave da API na tela Configuração da IA",
        ):
            obter_provedor(configuracao)

    def test_enterprise_sem_projeto_levanta_erro_configuracao(self):
        configuracao = ConfiguracaoIA.objects.create(
            pk=1,
            modo_acesso=ConfiguracaoIA.MODO_ENTERPRISE,
        )
        with self.assertRaisesMessage(
            ErroConfiguracao,
            "Preencha o ID do projeto no Google Cloud",
        ):
            obter_provedor(configuracao)

    def test_configuracao_valida_modo_api_key(self):
        configuracao = ConfiguracaoIA(modo_acesso=ConfiguracaoIA.MODO_API_KEY)
        with self.assertRaisesMessage(
            ValidationError,
            "Preencha a Chave da API na tela Configuração da IA",
        ):
            configuracao.full_clean()

    def test_configuracao_valida_modo_enterprise(self):
        configuracao = ConfiguracaoIA(modo_acesso=ConfiguracaoIA.MODO_ENTERPRISE)
        with self.assertRaisesMessage(
            ValidationError,
            "Preencha o ID do projeto no Google Cloud",
        ):
            configuracao.full_clean()

    @patch("ia.provedores.gemini.genai.Client")
    def test_provedor_falso_ignora_acesso_sem_chave(self, cliente):
        configuracao = ConfiguracaoIA.objects.create(pk=1, provedor="falso")

        provedor = obter_provedor(configuracao)

        self.assertIsInstance(provedor, ProvedorFalso)
        cliente.assert_not_called()

    @patch("ia.provedores.gemini.genai.Client")
    def test_enterprise_cria_cliente_sem_passar_api_key(self, cliente):
        configuracao = ConfiguracaoIA.objects.create(
            pk=1,
            modo_acesso=ConfiguracaoIA.MODO_ENTERPRISE,
            projeto_gcp="projeto-teste",
            regiao="global",
            api_key="nao-usada",
        )

        obter_provedor(configuracao)

        cliente.assert_called_once()
        argumentos = cliente.call_args.kwargs
        self.assertTrue(argumentos["enterprise"])
        self.assertEqual(argumentos["project"], "projeto-teste")
        self.assertEqual(argumentos["location"], "global")
        self.assertNotIn("api_key", argumentos)

    def test_str_configuracao_nao_contem_chave(self):
        configuracao = ConfiguracaoIA(
            provedor="gemini",
            api_key="chave-secreta",
        )

        self.assertNotIn("chave-secreta", str(configuracao))

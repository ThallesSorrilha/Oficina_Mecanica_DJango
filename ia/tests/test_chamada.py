from datetime import date
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from PIL import Image
from pypdf import PdfWriter

from ia.arquivos import ArquivoInvalido, hash_arquivo, preparar_arquivo
from ia.chamada import chamar_ia, testar_conexao
from ia.cota import CotaExcedida, mes_atual, situacao_da_cota
from ia.models import ConfiguracaoIA, ConfiguracaoIAUsuario, ConsumoIA, RequisicaoIA
from ia.provedores.base import ErroConfiguracao, ErroTemporario, PedidoIA, UsoTokens
from ia.provedores.falso import ProvedorFalso


class ChamadaTests(TestCase):
    def setUp(self):
        cache.clear()
        self.usuario = get_user_model().objects.create_user("teste")
        self.config = ConfiguracaoIA.objects.create(
            pk=1,
            provedor=ConfiguracaoIA.PROVEDOR_FALSO,
            limite_mensal_usuario=100000,
            reserva_minima_tokens=0,
            tentativas=2,
        )

    def pedido(self, config):
        from ia.provedores.base import PedidoIA

        return PedidoIA("instruções", "texto")

    def chamar(self, provedor, **kwargs):
        with patch("ia.chamada.obter_provedor", return_value=provedor):
            return chamar_ia(
                finalidade="app_teste",
                montar_pedido=self.pedido,
                usuario=self.usuario,
                **kwargs,
            )

    def test_sucesso_audita_referencia_e_soma_consumo(self):
        provedor = ProvedorFalso(self.config)
        provedor.programar(
            texto="resposta",
            uso=UsoTokens(entrada=10, saida=5, raciocinio=2),
        )

        resposta = self.chamar(provedor, referencia=self.usuario)

        self.assertEqual(resposta.texto, "resposta")
        auditoria = RequisicaoIA.objects.get()
        self.assertEqual(auditoria.situacao, "sucesso")
        self.assertEqual(auditoria.referencia, self.usuario)
        consumo = ConsumoIA.objects.get(dono=self.usuario, mes=mes_atual())
        self.assertEqual(consumo.tokens_total, 15)
        self.assertEqual(consumo.tokens_saida, 5)

    @patch("ia.chamada.time.sleep")
    def test_erro_temporario_seguido_de_sucesso_audita_duas_tentativas(self, dormir):
        provedor = ProvedorFalso(self.config)
        provedor.programar(erro=ErroTemporario("temporário"))
        provedor.programar(texto="ok", uso=UsoTokens(entrada=2, saida=3))

        self.chamar(provedor)

        self.assertEqual(
            list(RequisicaoIA.objects.values_list("tentativa", "situacao")),
            [(1, "erro_temporario"), (2, "sucesso")],
        )
        dormir.assert_called_once_with(1)

    def test_erro_configuracao_nao_repete(self):
        provedor = ProvedorFalso(self.config)
        erro = ErroConfiguracao("configuração inválida")
        provedor.programar(erro=erro)

        with self.assertRaises(ErroConfiguracao):
            self.chamar(provedor)

        self.assertEqual(RequisicaoIA.objects.count(), 1)
        self.assertEqual(RequisicaoIA.objects.get().tentativa, 1)

    def test_cota_esgotada_nao_chama_provedor_e_audita_bloqueio(self):
        self.config.limite_mensal_usuario = 10
        self.config.save()
        ConsumoIA.objects.create(dono=self.usuario, mes=mes_atual(), tokens_total=10)
        self.assertEqual(ConfiguracaoIA.obter().limite_mensal_usuario, 10)
        self.assertTrue(situacao_da_cota(self.usuario).esgotada)
        provedor = ProvedorFalso(self.config)

        with patch("ia.chamada.obter_provedor", return_value=provedor):
            with self.assertRaises(CotaExcedida):
                chamar_ia(
                    finalidade="app_teste",
                    montar_pedido=self.pedido,
                    usuario=self.usuario,
                )

        self.assertEqual(provedor.pedidos, [])
        self.assertEqual(RequisicaoIA.objects.get().situacao, "bloqueada_cota")

    def test_limite_proprio_zero_bloqueia_e_vazio_usa_padrao(self):
        ConfiguracaoIAUsuario.objects.create(
            usuario=self.usuario,
            limite_mensal=0,
        )
        with self.assertRaises(CotaExcedida):
            self.chamar(ProvedorFalso(self.config))
        self.assertEqual(RequisicaoIA.objects.get().situacao, "bloqueada_cota")

        RequisicaoIA.objects.all().delete()
        ConsumoIA.objects.all().delete()
        configuracao_usuario = ConfiguracaoIAUsuario.objects.get(usuario=self.usuario)
        configuracao_usuario.limite_mensal = None
        configuracao_usuario.save()
        provedor = ProvedorFalso(self.config)
        provedor.programar(uso=UsoTokens(entrada=1))
        self.chamar(provedor)
        self.assertEqual(ConsumoIA.objects.get().tokens_total, 1)

    def test_falha_ao_gravar_auditoria_nao_destroi_chamada(self):
        provedor = ProvedorFalso(self.config)
        provedor.programar(texto="ok", uso=UsoTokens(entrada=2))

        with patch("ia.chamada.RequisicaoIA.objects.create", side_effect=RuntimeError):
            resposta = self.chamar(provedor)

        self.assertEqual(resposta.texto, "ok")
        self.assertEqual(ConsumoIA.objects.get().tokens_total, 2)

    def test_teto_do_sistema_bloqueia(self):
        self.config.limite_mensal_sistema = 1
        self.config.save()
        ConsumoIA.objects.create(dono=self.usuario, mes=mes_atual(), tokens_total=1)
        provedor = ProvedorFalso(self.config)

        with patch("ia.chamada.obter_provedor", return_value=provedor):
            with self.assertRaisesMessage(Exception, "limite mensal do sistema"):
                chamar_ia(
                    finalidade="app_teste",
                    montar_pedido=self.pedido,
                    usuario=self.usuario,
                )

        self.assertEqual(provedor.pedidos, [])
        self.assertEqual(RequisicaoIA.objects.get().situacao, "indisponivel")

    def test_consumo_mes_anterior_nao_conta(self):
        ConsumoIA.objects.create(
            dono=self.usuario,
            mes=date(2020, 1, 1),
            tokens_total=100000,
        )
        provedor = ProvedorFalso(self.config)
        provedor.programar(uso=UsoTokens(entrada=1))

        self.chamar(provedor)

        self.assertEqual(
            ConsumoIA.objects.get(dono=self.usuario, mes=mes_atual()).tokens_total,
            1,
        )


class ArquivosTests(TestCase):
    def setUp(self):
        cache.clear()
        ConfiguracaoIA.objects.create(pk=1, tamanho_maximo_mb=1, pdf_max_paginas=1)

    def test_arquivo_acima_do_tamanho_maximo_e_recusado(self):
        with self.assertRaisesMessage(ArquivoInvalido, "tamanho máximo"):
            preparar_arquivo(b"x" * (1024 * 1024 + 1), "image/png")

    def test_tipo_nao_permitido_e_recusado(self):
        with self.assertRaisesMessage(ArquivoInvalido, "Tipo de arquivo não permitido"):
            preparar_arquivo(b"texto", "text/plain")

    def test_imagem_vira_jpeg_rgb_reduzida(self):
        buffer = BytesIO()
        Image.new("RGBA", (4000, 2000), (255, 0, 0, 128)).save(buffer, format="PNG")

        conteudo, mime = preparar_arquivo(buffer.getvalue(), "image/png", lado_maximo=500)

        self.assertEqual(mime, "image/jpeg")
        with Image.open(BytesIO(conteudo)) as imagem:
            self.assertEqual(imagem.mode, "RGB")
            self.assertLessEqual(max(imagem.size), 500)

    def test_pdf_acima_do_limite_de_paginas_e_recusado(self):
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        writer.add_blank_page(width=200, height=200)
        buffer = BytesIO()
        writer.write(buffer)

        with self.assertRaisesMessage(ArquivoInvalido, "número máximo de páginas"):
            preparar_arquivo(buffer.getvalue(), "application/pdf")

    def test_hash_arquivo_e_sha256_hexadecimal(self):
        self.assertEqual(
            hash_arquivo(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )


class TestarConexaoTests(TestCase):
    def setUp(self):
        cache.clear()
        self.usuario = get_user_model().objects.create_user("conexao")
        self.config = ConfiguracaoIA.objects.create(
            pk=1,
            provedor=ConfiguracaoIA.PROVEDOR_FALSO,
            limite_mensal_sistema=0,
            reserva_minima_tokens=0,
        )

    def test_testar_conexao_informa_modo_api_key(self):
        provedor = ProvedorFalso(self.config)
        with patch("ia.chamada.obter_provedor", return_value=provedor):
            _, mensagem = testar_conexao(self.usuario)

        self.assertEqual(mensagem, "Conexão realizada usando API Key.")
        self.assertEqual(provedor.pedidos[0].esquema.__name__, "RespostaTeste")
        self.assertEqual(
            RequisicaoIA.objects.get().finalidade,
            "teste_conexao",
        )

    def test_testar_conexao_informa_projeto_e_regiao_no_enterprise(self):
        self.config.modo_acesso = ConfiguracaoIA.MODO_ENTERPRISE
        self.config.projeto_gcp = "projeto-x"
        self.config.regiao = "us-central1"
        self.config.save()
        provedor = ProvedorFalso(self.config)
        with patch("ia.chamada.obter_provedor", return_value=provedor):
            _, mensagem = testar_conexao(self.usuario)

        self.assertEqual(
            mensagem,
            "Conexão realizada usando Enterprise (projeto-x, região us-central1).",
        )


class FluxoExemploChamadaIATests(TestCase):
    def setUp(self):
        cache.clear()
        self.usuario = get_user_model().objects.create_user(
            username="usuario-fluxo",
        )
        self.config = ConfiguracaoIA.objects.create(
            pk=1,
            provedor=ConfiguracaoIA.PROVEDOR_FALSO,
            limite_mensal_usuario=100000,
            limite_mensal_sistema=0,
            reserva_minima_tokens=0,
        )
        self.provedor = ProvedorFalso(self.config)
        self.provedor.programar(
            texto="conexão funcionando.",
            uso=UsoTokens(entrada=8, saida=3),
        )

    def test_exemplo_de_chamada_ia_com_usuario_autenticado(self):
        def montar_pedido(config):
            return PedidoIA(
                instrucoes="Responda somente em português.",
                texto="Diga apenas: conexão funcionando.",
            )

        with patch("ia.chamada.obter_provedor", return_value=self.provedor):
            resposta = chamar_ia(
                finalidade="app_teste",
                montar_pedido=montar_pedido,
                usuario=self.usuario,
                origem="comando",
                versao_prompt="v1",
            )

        self.assertEqual(resposta.texto, "conexão funcionando.")
        self.assertEqual(len(self.provedor.pedidos), 1)
        self.assertEqual(
            self.provedor.pedidos[0].instrucoes,
            "Responda somente em português.",
        )
        self.assertEqual(
            self.provedor.pedidos[0].texto,
            "Diga apenas: conexão funcionando.",
        )
        auditoria = RequisicaoIA.objects.get()
        self.assertEqual(auditoria.usuario, self.usuario)
        self.assertEqual(auditoria.finalidade, "app_teste")
        self.assertEqual(auditoria.origem, "comando")
        self.assertEqual(auditoria.versao_prompt, "v1")
        self.assertEqual(auditoria.situacao, "sucesso")

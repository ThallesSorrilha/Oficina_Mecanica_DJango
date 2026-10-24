from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from ia.models import ConfiguracaoIA, RequisicaoIA


class TelasIATests(TestCase):
    def setUp(self):
        cache.clear()
        self.configuracao = ConfiguracaoIA.objects.create(
            pk=1,
            provedor=ConfiguracaoIA.PROVEDOR_FALSO,
            limite_mensal_sistema=0,
            reserva_minima_tokens=0,
        )
        self.comum = get_user_model().objects.create_user(
            username="comum",
            password="senha-segura",
        )
        self.outro = get_user_model().objects.create_user(
            username="outro",
            password="senha-segura",
        )
        RequisicaoIA.objects.create(
            usuario=self.comum,
            finalidade="app_teste",
            situacao="sucesso",
            tokens_total=12,
            resposta="resposta própria",
        )
        RequisicaoIA.objects.create(
            usuario=self.outro,
            finalidade="app_outro",
            situacao="sucesso",
            tokens_total=99,
            resposta="resposta de outro usuário",
        )

    def test_usuario_comum_recebe_403_nas_telas_de_administracao(self):
        self.client.force_login(self.comum)

        for nome in ("ia:requisicoes", "ia:configuracao", "ia:usuarios"):
            with self.subTest(nome=nome):
                resposta = self.client.get(reverse(nome))
                self.assertEqual(resposta.status_code, 403)

    def test_usuario_comum_ve_apenas_o_proprio_consumo(self):
        self.client.force_login(self.comum)

        resposta = self.client.get(reverse("ia:consumo"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "app_teste")
        self.assertNotContains(resposta, "app_outro")
        self.assertNotContains(resposta, "resposta de outro usuário")

    def test_anonymous_e_redirecionado_para_login(self):
        for nome in (
            "ia:requisicoes",
            "ia:configuracao",
            "ia:usuarios",
            "ia:consumo",
        ):
            with self.subTest(nome=nome):
                resposta = self.client.get(reverse(nome))
                self.assertEqual(resposta.status_code, 302)
                self.assertIn("/login/", resposta.url)

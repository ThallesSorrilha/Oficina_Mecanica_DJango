from django.views.generic import TemplateView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from mecanica.models import OrdemServico


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chamados = OrdemServico.objects.select_related(
            "carro", "carro__cliente"
        ).prefetch_related(
            "ordem_servico_servicos__servico",
            "ordem_pecas__peca",
        )

        context["chamados"] = chamados[:8]
        context["chamados_abertos"] = chamados.exclude(
            estado__iexact="concluído"
        ).count()
        context["chamados_concluidos"] = chamados.filter(
            estado__iexact="concluído"
        ).count()
        context["veiculos_ativos"] = OrdemServico.objects.values(
            "carro_id"
        ).distinct().count()
        hoje = timezone.localdate()
        ordens_do_mes = OrdemServico.objects.filter(
            data_inicio__year=hoje.year,
            data_inicio__month=hoje.month,
        )
        context["faturamento_mes"] = sum(
            (ordem.total for ordem in ordens_do_mes),
            0,
        )
        return context


class ContatoView(TemplateView):
    template_name = "website/contato.html"


class SobreView(TemplateView):
    template_name = "website/sobre.html"


class SignUpView(CreateView):
    """
    View para cadastro de novos usuários.
    Usa o formulário UserCreationForm padrão do Django.
    """
    model = User
    form_class = UserCreationForm
    template_name = "website/signup.html"
    success_url = reverse_lazy("login")

from collections import Counter
from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, UpdateView
from django.views import View

from .chamada import testar_conexao
from .cota import limite_do_usuario, mes_atual, situacao_da_cota
from .forms import ConfiguracaoIAForm, ConfiguracaoIAUsuarioForm
from .models import ConfiguracaoIA, ConfiguracaoIAUsuario, ConsumoIA, RequisicaoIA


class SuperusuarioMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class RequisicaoIAListView(SuperusuarioMixin, ListView):
    model = RequisicaoIA
    template_name = "ia/requisicao_list.html"
    context_object_name = "requisicoes"
    paginate_by = 20

    def get_queryset(self):
        queryset = RequisicaoIA.objects.select_related(
            "usuario", "referencia_tipo"
        ).order_by("-criado_em")
        params = self.request.GET
        if params.get("usuario"):
            queryset = queryset.filter(usuario__username__icontains=params["usuario"])
        if params.get("situacao"):
            queryset = queryset.filter(situacao=params["situacao"])
        if params.get("finalidade"):
            queryset = queryset.filter(finalidade__icontains=params["finalidade"])
        if params.get("origem"):
            queryset = queryset.filter(origem=params["origem"])
        if params.get("de"):
            queryset = queryset.filter(criado_em__date__gte=params["de"])
        if params.get("ate"):
            queryset = queryset.filter(criado_em__date__lte=params["ate"])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inicio = mes_atual()
        mensal = RequisicaoIA.objects.filter(criado_em__date__gte=inicio)
        context["resumo_mes"] = mensal.aggregate(
            tokens=Sum("tokens_total"),
            custo=Sum("custo_estimado"),
            erros=Count("id", filter=~Q(situacao="sucesso")),
            quantidade=Count("id"),
        )
        referencias = Counter(
            str(item.referencia)
            for item in mensal
            if item.referencia is not None
        )
        usuarios = mensal.values("usuario__username").annotate(
            tokens=Sum("tokens_total")
        ).order_by("-tokens")[:5]
        context["top_referencias"] = referencias.most_common(5)
        context["top_usuarios"] = usuarios
        context["situacoes"] = RequisicaoIA.SITUACOES
        context["origens"] = RequisicaoIA.ORIGENS
        context["filtros"] = self.request.GET
        return context


class RequisicaoIADetailView(SuperusuarioMixin, DetailView):
    model = RequisicaoIA
    template_name = "ia/requisicao_detail.html"
    context_object_name = "requisicao"


class MeuConsumoView(LoginRequiredMixin, ListView):
    model = RequisicaoIA
    template_name = "ia/meu_consumo.html"
    context_object_name = "requisicoes"
    paginate_by = 20

    def get_queryset(self):
        return RequisicaoIA.objects.filter(
            usuario=self.request.user
        ).order_by("-criado_em")[:20]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["situacao_cota"] = situacao_da_cota(self.request.user)
        context["configuracao"] = ConfiguracaoIA.obter()
        return context


class ConfiguracaoIAUpdateView(SuperusuarioMixin, UpdateView):
    model = ConfiguracaoIA
    form_class = ConfiguracaoIAForm
    template_name = "ia/configuracao_form.html"
    success_url = reverse_lazy("ia:configuracao")
    context_object_name = "configuracao"

    def get_object(self, queryset=None):
        return ConfiguracaoIA.obter()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "testar_conexao" in request.POST:
            try:
                _, mensagem = testar_conexao(request.user)
            except Exception as exc:
                messages.error(request, f"Falha ao testar a conexão: {exc}")
            else:
                messages.success(request, mensagem)
            return redirect("ia:configuracao")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Configuração de IA salva com sucesso.")
        return super().form_valid(form)


class IAUsuarioListView(SuperusuarioMixin, ListView):
    model = get_user_model()
    template_name = "ia/usuario_list.html"
    context_object_name = "usuarios"
    paginate_by = 20

    def get_queryset(self):
        return get_user_model().objects.all().order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        configuracao = ConfiguracaoIA.obter()
        contexto_usuarios = []
        for usuario in context["usuarios"]:
            override = ConfiguracaoIAUsuario.objects.filter(usuario=usuario).first()
            consumo = ConsumoIA.objects.filter(
                dono=usuario, mes=mes_atual()
            ).first()
            contexto_usuarios.append({
                "usuario": usuario,
                "configuracao": override,
                "limite": override.limite_mensal if override and override.limite_mensal is not None else configuracao.limite_mensal_usuario,
                "tem_limite_proprio": bool(override and override.limite_mensal is not None),
                "uso": consumo.tokens_total if consumo else 0,
                "ligada": not override or override.ia_habilitada,
            })
        context["usuarios_ia"] = contexto_usuarios
        return context


class IAUsuarioUpdateView(SuperusuarioMixin, UpdateView):
    model = ConfiguracaoIAUsuario
    form_class = ConfiguracaoIAUsuarioForm
    template_name = "ia/usuario_form.html"
    context_object_name = "configuracao_usuario"

    def get_object(self, queryset=None):
        usuario = get_object_or_404(get_user_model(), pk=self.kwargs["usuario_id"])
        objeto, _ = ConfiguracaoIAUsuario.objects.get_or_create(usuario=usuario)
        return objeto

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.object.usuario
        return context

    def get_success_url(self):
        return reverse("ia:usuarios")

    def form_valid(self, form):
        messages.success(self.request, "Configuração do usuário salva com sucesso.")
        return super().form_valid(form)


class IAUsuarioPadraoView(SuperusuarioMixin, View):
    def post(self, request, usuario_id):
        usuario = get_object_or_404(get_user_model(), pk=usuario_id)
        ConfiguracaoIAUsuario.objects.filter(usuario=usuario).delete()
        messages.success(request, "O usuário voltou a usar os padrões da IA.")
        return redirect("ia:usuarios")

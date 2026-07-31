from django.views.generic import TemplateView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "website/index.html"


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

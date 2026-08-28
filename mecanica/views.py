from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.forms import modelform_factory

from .models import (
    Cliente, Carro, Servico, Peca, Mecanico,
    ConsultorTecnico, OrdemServico, OrdemPecas
)

from .forms import BaseModelForm, OrdemPecasForm, OrdemServicoForm, OrdemServicoServicoForm


class BaseListView(LoginRequiredMixin, ListView):
    paginate_by = 3
    list_columns = []
    detail_url_name = None
    create_url_name = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        columns = self.list_columns or [("Descricao", None)]
        ctx["columns"] = columns
        ctx["detail_url_name"] = self.detail_url_name
        ctx["create_url_name"] = self.create_url_name
        ctx["rows"] = [
            {
                "pk": obj.pk,
                "values": [str(obj) if field is None else getattr(obj, field) for _, field in columns],
            }
            for obj in ctx["object_list"]
        ]
        return ctx


class BaseDetailView(LoginRequiredMixin, DetailView):
    edit_url_name = None
    delete_url_name = None

    def get_default_detail_fields(self):
        fields = []
        for field in self.model._meta.fields:
            if field.name == "id":
                continue
            fields.append((field.verbose_name.title(), field.name))
        return fields

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        fields = self.get_default_detail_fields()
        ctx["detail_rows"] = [
            {"label": label, "value": getattr(ctx["object"], field)}
            for label, field in fields
        ]
        ctx["edit_url_name"] = self.edit_url_name
        ctx["delete_url_name"] = self.delete_url_name
        if self.model is OrdemServico:
            ctx["servico_items"] = ctx["object"].ordem_servico_servicos.select_related(
                "servico"
            )
            ctx["peca_items"] = ctx["object"].ordem_pecas.select_related(
                "peca"
            )
            ctx["total"] = ctx["object"].total
        return ctx


class BaseCreateView(LoginRequiredMixin, CreateView):
    def get_form_class(self):
        if self.form_class is not None:
            return self.form_class
        exclude = getattr(self, "exclude_fields", ["id"])
        return modelform_factory(self.model, exclude=exclude, form=BaseModelForm)


class BaseUpdateView(LoginRequiredMixin, UpdateView):
    def get_form_class(self):
        if self.form_class is not None:
            return self.form_class
        exclude = getattr(self, "exclude_fields", ["id"])
        return modelform_factory(self.model, exclude=exclude, form=BaseModelForm)


class BaseFuncionarioCreateView(BaseCreateView):
    pass


class BaseFuncionarioUpdateView(BaseUpdateView):
    pass


class BaseFuncionarioListView(BaseListView):
    list_columns = [
        ("Nome", "nome"),
        ("CPF", "cpf"),
        ("Telefone", "telefone"),
        ("Horas Sem.", "horas_semanais"),
    ]


class BaseDeleteView(LoginRequiredMixin, DeleteView):
    pass

# =========================
# Cliente
# =========================


class ClienteCreate(BaseCreateView):
    model = Cliente
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('cliente-list')
    extra_context = {'titulo': 'Cadastro de Cliente', 'botao': 'Criar Cliente'}


class ClienteUpdate(BaseUpdateView):
    model = Cliente
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('cliente-list')
    extra_context = {'titulo': 'Editar dados do Cliente',
                     'botao': 'Atualizar Cliente'}


class ClienteDelete(BaseDeleteView):
    model = Cliente
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('cliente-list')
    extra_context = {'titulo': 'Excluir Cliente', 'botao': 'Sim, excluir!'}


class ClienteList(BaseListView):
    model = Cliente
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Clientes',
                     'cadastro': '+ Adicionar Cliente'}
    detail_url_name = 'cliente-detail'
    create_url_name = 'cliente-create'
    list_columns = [
        ("Nome", "nome"),
        ("CPF", "cpf"),
        ("Nascimento", "data_nascimento"),
        ("Telefone", "telefone"),
    ]


class ClienteDetail(BaseDetailView):
    model = Cliente
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Cliente'}
    edit_url_name = 'cliente-update'
    delete_url_name = 'cliente-delete'


# =========================
# Carro
# =========================
class CarroCreate(BaseCreateView):
    model = Carro
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('carro-list')
    extra_context = {'titulo': 'Cadastro de Carro', 'botao': 'Criar Carro'}


class CarroUpdate(BaseUpdateView):
    model = Carro
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('carro-list')
    extra_context = {'titulo': 'Editar dados do Carro',
                     'botao': 'Atualizar Carro'}


class CarroDelete(BaseDeleteView):
    model = Carro
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('carro-list')
    extra_context = {'titulo': 'Excluir Carro', 'botao': 'Sim, excluir!'}


class CarroList(BaseListView):
    model = Carro
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Carros',
                     'cadastro': '+ Adicionar Carro'}
    detail_url_name = 'carro-detail'
    create_url_name = 'carro-create'
    list_columns = [
        ("Modelo", "modelo"),
        ("Cor", "cor"),
        ("Ano", "ano"),
        ("Placa", "placa"),
    ]


class CarroDetail(BaseDetailView):
    model = Carro
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Carro'}
    edit_url_name = 'carro-update'
    delete_url_name = 'carro-delete'


# =========================
# Servico
# =========================
class ServicoCreate(BaseCreateView):
    model = Servico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('servico-list')
    extra_context = {'titulo': 'Cadastro de Serviço', 'botao': 'Criar Serviço'}


class ServicoUpdate(BaseUpdateView):
    model = Servico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('servico-list')
    extra_context = {'titulo': 'Editar dados do Serviço',
                     'botao': 'Atualizar Serviço'}


class ServicoDelete(BaseDeleteView):
    model = Servico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('servico-list')
    extra_context = {'titulo': 'Excluir Serviço', 'botao': 'Sim, excluir!'}


class ServicoList(BaseListView):
    model = Servico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Serviços',
                     'cadastro': '+ Adicionar Serviço'}
    detail_url_name = 'servico-detail'
    create_url_name = 'servico-create'
    list_columns = [
        ("Nome", "nome"),
        ("Descricao", "descricao"),
        ("Preco", "preco"),
    ]


class ServicoDetail(BaseDetailView):
    model = Servico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Serviço'}
    edit_url_name = 'servico-update'
    delete_url_name = 'servico-delete'


# =========================
# Peca
# =========================
class PecaCreate(BaseCreateView):
    model = Peca
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('peca-list')
    extra_context = {'titulo': 'Cadastro de Peça', 'botao': 'Criar Peça'}


class PecaUpdate(BaseUpdateView):
    model = Peca
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('peca-list')
    extra_context = {'titulo': 'Editar dados da Peça',
                     'botao': 'Atualizar Peça'}


class PecaDelete(BaseDeleteView):
    model = Peca
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('peca-list')
    extra_context = {'titulo': 'Excluir Peça', 'botao': 'Sim, excluir!'}


class PecaList(BaseListView):
    model = Peca
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Peças',
                     'cadastro': '+ Adicionar Peça'}
    detail_url_name = 'peca-detail'
    create_url_name = 'peca-create'
    list_columns = [
        ("Nome", "nome"),
        ("Fabricante", "fabricante"),
        ("Preco", "preco"),
        ("Estoque", "estoque"),
    ]


class PecaDetail(BaseDetailView):
    model = Peca
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes da Peça'}
    edit_url_name = 'peca-update'
    delete_url_name = 'peca-delete'


# =========================
# Mecanico
# =========================
class MecanicoCreate(BaseFuncionarioCreateView):
    model = Mecanico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('mecanico-list')
    extra_context = {'titulo': 'Cadastro de Mecânico',
                     'botao': 'Criar Mecânico'}


class MecanicoUpdate(BaseFuncionarioUpdateView):
    model = Mecanico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('mecanico-list')
    extra_context = {'titulo': 'Editar dados do Mecânico',
                     'botao': 'Atualizar Mecânico'}


class MecanicoDelete(BaseDeleteView):
    model = Mecanico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('mecanico-list')
    extra_context = {'titulo': 'Excluir Mecânico', 'botao': 'Sim, excluir!'}


class MecanicoList(BaseFuncionarioListView):
    model = Mecanico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Mecânicos',
                     'cadastro': '+ Adicionar Mecânico'}
    detail_url_name = 'mecanico-detail'
    create_url_name = 'mecanico-create'


class MecanicoDetail(BaseDetailView):
    model = Mecanico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Mecânico'}
    edit_url_name = 'mecanico-update'
    delete_url_name = 'mecanico-delete'


# =========================
# ConsultorTecnico
# =========================
class ConsultorTecnicoCreate(BaseFuncionarioCreateView):
    model = ConsultorTecnico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('consultor-tecnico-list')
    extra_context = {'titulo': 'Cadastro de Consultor Técnico',
                     'botao': 'Criar Consultor Técnico'}


class ConsultorTecnicoUpdate(BaseFuncionarioUpdateView):
    model = ConsultorTecnico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('consultor-tecnico-list')
    extra_context = {'titulo': 'Editar dados do Consultor Técnico',
                     'botao': 'Atualizar Consultor Técnico'}


class ConsultorTecnicoDelete(BaseDeleteView):
    model = ConsultorTecnico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('consultor-tecnico-list')
    extra_context = {'titulo': 'Excluir Consultor Técnico',
                     'botao': 'Sim, excluir!'}


class ConsultorTecnicoList(BaseFuncionarioListView):
    model = ConsultorTecnico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Consultores Técnicos',
                     'cadastro': '+ Adicionar Consultor Técnico'}
    detail_url_name = 'consultor-tecnico-detail'
    create_url_name = 'consultor-tecnico-create'


class ConsultorTecnicoDetail(BaseDetailView):
    model = ConsultorTecnico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Consultor Técnico'}
    edit_url_name = 'consultor-tecnico-update'
    delete_url_name = 'consultor-tecnico-delete'


# =========================
# OrdemServico
# =========================
class OrdemServicoCreate(BaseCreateView):
    model = OrdemServico
    form_class = OrdemServicoForm
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-servico-list')
    extra_context = {'titulo': 'Cadastro de Ordem de Serviço',
                     'botao': 'Criar Ordem de Serviço'}


class OrdemServicoUpdate(BaseUpdateView):
    model = OrdemServico
    form_class = OrdemServicoForm
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-servico-list')
    extra_context = {'titulo': 'Editar dados da Ordem de Serviço',
                     'botao': 'Atualizar Ordem de Serviço'}


class OrdemServicoDelete(BaseDeleteView):
    model = OrdemServico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-servico-list')
    extra_context = {'titulo': 'Excluir Ordem de Serviço',
                     'botao': 'Sim, excluir!'}


class OrdemServicoList(BaseListView):
    model = OrdemServico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Ordens de Serviço',
                     'cadastro': '+ Adicionar Ordem de Serviço'}
    detail_url_name = 'ordem-servico-detail'
    create_url_name = 'ordem-servico-create'
    list_columns = [
        ("Estado", "estado"),
        ("Total", "total"),
        ("Consultor Técnico", "consultor_tecnico"),
        ("Data Término", "data_termino"),
    ]


class OrdemServicoDetail(BaseDetailView):
    model = OrdemServico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes da Ordem de Serviço'}
    edit_url_name = 'ordem-servico-update'
    delete_url_name = 'ordem-servico-delete'


# =========================
# OrdemPecas
# =========================
class OrdemPecasCreate(BaseCreateView):
    model = OrdemPecas
    form_class = OrdemPecasForm
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-pecas-list')
    extra_context = {'titulo': 'Cadastro de Ordem de Peças',
                     'botao': 'Criar Ordem de Peças'}


class OrdemPecasUpdate(BaseUpdateView):
    model = OrdemPecas
    form_class = OrdemPecasForm
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-pecas-list')
    extra_context = {'titulo': 'Editar dados da Ordem de Peças',
                     'botao': 'Atualizar Ordem de Peças'}


class OrdemPecasDelete(BaseDeleteView):
    model = OrdemPecas
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-pecas-list')
    extra_context = {'titulo': 'Excluir Ordem de Peças',
                     'botao': 'Sim, excluir!'}


class OrdemPecasList(BaseListView):
    model = OrdemPecas
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Ordens de Peças',
                     'cadastro': '+ Adicionar Ordem de Peças'}
    detail_url_name = 'ordem-pecas-detail'
    create_url_name = 'ordem-pecas-create'
    list_columns = [
        ("Peça", "peca"),
        ("Ordem Serviço", "ordem_servico"),
        ("Quantidade", "quantidade"),
        ("Preço Unitário", "preco_unitario"),
    ]


class OrdemPecasDetail(BaseDetailView):
    model = OrdemPecas
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes da Ordem de Peças'}
    edit_url_name = 'ordem-pecas-update'
    delete_url_name = 'ordem-pecas-delete'

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from .models import (
    Cliente, Carro, Servico, Peca, Funcionario, Mecanico,
    ConsultorTecnico, OrdemServico, OrdemPecas
)

from .forms import (
    ClienteForm
)

from .details import (
    CLIENTE_DETAIL_FIELDS
)


class BaseListView(ListView):
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


class BaseDetailView(DetailView):
    detail_fields = []
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
        fields = self.detail_fields or self.get_default_detail_fields()
        ctx["detail_rows"] = [
            {"label": label, "value": getattr(ctx["object"], field)}
            for label, field in fields
        ]
        ctx["edit_url_name"] = self.edit_url_name
        ctx["delete_url_name"] = self.delete_url_name
        return ctx

# =========================
# Cliente
# =========================


class ClienteCreate(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('cliente-list')
    extra_context = {'titulo': 'Cadastro de Cliente', 'botao': 'Criar Cliente'}


class ClienteUpdate(UpdateView):
    model = Cliente
    fields = ['nome', 'cpf', 'data_nascimento', 'telefone']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('cliente-list')
    extra_context = {'titulo': 'Editar dados do Cliente',
                     'botao': 'Atualizar Cliente'}


class ClienteDelete(DeleteView):
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
    detail_fields = CLIENTE_DETAIL_FIELDS
    edit_url_name = 'cliente-update'
    delete_url_name = 'cliente-delete'


# =========================
# Carro
# =========================
class CarroCreate(CreateView):
    model = Carro
    fields = ['vin', 'placa', 'modelo', 'cor',
              'ano', 'quilometragem', 'cliente']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('carro-list')
    extra_context = {'titulo': 'Cadastro de Carro', 'botao': 'Criar Carro'}


class CarroUpdate(UpdateView):
    model = Carro
    fields = ['vin', 'placa', 'modelo', 'cor',
              'ano', 'quilometragem', 'cliente']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('carro-list')
    extra_context = {'titulo': 'Editar dados do Carro',
                     'botao': 'Atualizar Carro'}


class CarroDelete(DeleteView):
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
class ServicoCreate(CreateView):
    model = Servico
    fields = ['nome', 'descricao', 'preco']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('servico-list')
    extra_context = {'titulo': 'Cadastro de Serviço', 'botao': 'Criar Serviço'}


class ServicoUpdate(UpdateView):
    model = Servico
    fields = ['nome', 'descricao', 'preco']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('servico-list')
    extra_context = {'titulo': 'Editar dados do Serviço',
                     'botao': 'Atualizar Serviço'}


class ServicoDelete(DeleteView):
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
class PecaCreate(CreateView):
    model = Peca
    fields = ['nome', 'fabricante', 'codigo', 'descricao', 'preco', 'estoque']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('peca-list')
    extra_context = {'titulo': 'Cadastro de Peça', 'botao': 'Criar Peça'}


class PecaUpdate(UpdateView):
    model = Peca
    fields = ['nome', 'fabricante', 'codigo', 'descricao', 'preco', 'estoque']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('peca-list')
    extra_context = {'titulo': 'Editar dados da Peça',
                     'botao': 'Atualizar Peça'}


class PecaDelete(DeleteView):
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
# Funcionario
# =========================
class FuncionarioCreate(CreateView):
    model = Funcionario
    fields = ['nome', 'cpf', 'data_nascimento',
              'telefone', 'cargo', 'salario', 'horas_semanais']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('funcionario-list')
    extra_context = {'titulo': 'Cadastro de Funcionário',
                     'botao': 'Criar Funcionário'}


class FuncionarioUpdate(UpdateView):
    model = Funcionario
    fields = ['nome', 'cpf', 'data_nascimento',
              'telefone', 'cargo', 'salario', 'horas_semanais']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('funcionario-list')
    extra_context = {'titulo': 'Editar dados do Funcionário',
                     'botao': 'Atualizar Funcionário'}


class FuncionarioDelete(DeleteView):
    model = Funcionario
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('funcionario-list')
    extra_context = {'titulo': 'Excluir Funcionário', 'botao': 'Sim, excluir!'}


class FuncionarioList(BaseListView):
    model = Funcionario
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Funcionários',
                     'cadastro': '+ Adicionar Funcionário'}
    detail_url_name = 'funcionario-detail'
    create_url_name = 'funcionario-create'
    list_columns = [
        ("Nome", "nome"),
        ("Cargo", "cargo"),
        ("Horas Sem.", "horas_semanais"),
        ("Telefone", "telefone"),
    ]


class FuncionarioDetail(BaseDetailView):
    model = Funcionario
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Funcionário'}
    edit_url_name = 'funcionario-update'
    delete_url_name = 'funcionario-delete'


# =========================
# Mecanico
# =========================
class MecanicoCreate(CreateView):
    model = Mecanico
    fields = ['nome', 'cpf', 'data_nascimento', 'telefone',
              'cargo', 'salario', 'horas_semanais', 'especialidade']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('mecanico-list')
    extra_context = {'titulo': 'Cadastro de Mecânico',
                     'botao': 'Criar Mecânico'}


class MecanicoUpdate(UpdateView):
    model = Mecanico
    fields = ['nome', 'cpf', 'data_nascimento', 'telefone',
              'cargo', 'salario', 'horas_semanais', 'especialidade']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('mecanico-list')
    extra_context = {'titulo': 'Editar dados do Mecânico',
                     'botao': 'Atualizar Mecânico'}


class MecanicoDelete(DeleteView):
    model = Mecanico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('mecanico-list')
    extra_context = {'titulo': 'Excluir Mecânico', 'botao': 'Sim, excluir!'}


class MecanicoList(BaseListView):
    model = Mecanico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Mecânicos',
                     'cadastro': '+ Adicionar Mecânico'}
    detail_url_name = 'mecanico-detail'
    create_url_name = 'mecanico-create'
    list_columns = [
        ("Nome", "nome"),
        ("Especialidade", "especialidade"),
    ]


class MecanicoDetail(BaseDetailView):
    model = Mecanico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Mecânico'}
    edit_url_name = 'mecanico-update'
    delete_url_name = 'mecanico-delete'


# =========================
# ConsultorTecnico
# =========================
class ConsultorTecnicoCreate(CreateView):
    model = ConsultorTecnico
    fields = ['nome', 'cpf', 'data_nascimento',
              'telefone', 'cargo', 'salario', 'horas_semanais']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('consultor-tecnico-list')
    extra_context = {'titulo': 'Cadastro de Consultor Técnico',
                     'botao': 'Criar Consultor Técnico'}


class ConsultorTecnicoUpdate(UpdateView):
    model = ConsultorTecnico
    fields = ['nome', 'cpf', 'data_nascimento',
              'telefone', 'cargo', 'salario', 'horas_semanais']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('consultor-tecnico-list')
    extra_context = {'titulo': 'Editar dados do Consultor Técnico',
                     'botao': 'Atualizar Consultor Técnico'}


class ConsultorTecnicoDelete(DeleteView):
    model = ConsultorTecnico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('consultor-tecnico-list')
    extra_context = {'titulo': 'Excluir Consultor Técnico',
                     'botao': 'Sim, excluir!'}


class ConsultorTecnicoList(BaseListView):
    model = ConsultorTecnico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Consultores Técnicos',
                     'cadastro': '+ Adicionar Consultor Técnico'}
    detail_url_name = 'consultor-tecnico-detail'
    create_url_name = 'consultor-tecnico-create'
    list_columns = [
        ("Nome", "nome"),
    ]


class ConsultorTecnicoDetail(BaseDetailView):
    model = ConsultorTecnico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Consultor Técnico'}
    edit_url_name = 'consultor-tecnico-update'
    delete_url_name = 'consultor-tecnico-delete'


# =========================
# OrdemServico
# =========================
class OrdemServicoCreate(CreateView):
    model = OrdemServico
    fields = [
        'estado', 'preco', 'previsao_termino', 'data_termino', 'descricao',
        'observacao', 'carro', 'consultorTecnico', 'mecanicos', 'servicos'
    ]
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-servico-list')
    extra_context = {'titulo': 'Cadastro de Ordem de Serviço',
                     'botao': 'Criar Ordem de Serviço'}


class OrdemServicoUpdate(UpdateView):
    model = OrdemServico
    fields = [
        'estado', 'preco', 'previsao_termino', 'data_termino', 'descricao',
        'observacao', 'carro', 'consultorTecnico', 'mecanicos', 'servicos'
    ]
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-servico-list')
    extra_context = {'titulo': 'Editar dados da Ordem de Serviço',
                     'botao': 'Atualizar Ordem de Serviço'}


class OrdemServicoDelete(DeleteView):
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
        ("Preco", "preco"),
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
class OrdemPecasCreate(CreateView):
    model = OrdemPecas
    fields = ['peca', 'ordem_servico', 'quantidade', 'preco']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-pecas-list')
    extra_context = {'titulo': 'Cadastro de Ordem de Peças',
                     'botao': 'Criar Ordem de Peças'}


class OrdemPecasUpdate(UpdateView):
    model = OrdemPecas
    fields = ['peca', 'ordem_servico', 'quantidade', 'preco']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('ordem-pecas-list')
    extra_context = {'titulo': 'Editar dados da Ordem de Peças',
                     'botao': 'Atualizar Ordem de Peças'}


class OrdemPecasDelete(DeleteView):
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
        ("Preço", "preco"),
    ]


class OrdemPecasDetail(BaseDetailView):
    model = OrdemPecas
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes da Ordem de Peças'}
    edit_url_name = 'ordem-pecas-update'
    delete_url_name = 'ordem-pecas-delete'

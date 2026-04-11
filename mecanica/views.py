from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from .models import (
    Cliente, Carro, Servico, Peca, Funcionario, Mecanico,
    ConsultorTecnico, OrdemServico, OrdemPecas
)


# =========================
# Cliente
# =========================
class ClienteCreate(CreateView):
    model = Cliente
    fields = ['nome', 'cpf', 'data_nascimento', 'telefone']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Cliente', 'botao': 'Criar Cliente'}


class ClienteUpdate(UpdateView):
    model = Cliente
    fields = ['nome', 'cpf', 'data_nascimento', 'telefone']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados do Cliente',
                     'botao': 'Atualizar Cliente'}


class ClienteDelete(DeleteView):
    model = Cliente
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Cliente', 'botao': 'Sim, excluir!'}


class ClienteList(ListView):
    model = Cliente
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Clientes'}


class ClienteDetail(DetailView):
    model = Cliente
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Cliente'}


# =========================
# Carro
# =========================
class CarroCreate(CreateView):
    model = Carro
    fields = ['vin', 'placa', 'modelo', 'cor',
              'ano', 'quilometragem', 'cliente']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Carro', 'botao': 'Criar Carro'}


class CarroUpdate(UpdateView):
    model = Carro
    fields = ['vin', 'placa', 'modelo', 'cor',
              'ano', 'quilometragem', 'cliente']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados do Carro',
                     'botao': 'Atualizar Carro'}


class CarroDelete(DeleteView):
    model = Carro
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Carro', 'botao': 'Sim, excluir!'}


class CarroList(ListView):
    model = Carro
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Carros'}


class CarroDetail(DetailView):
    model = Carro
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Carro'}


# =========================
# Servico
# =========================
class ServicoCreate(CreateView):
    model = Servico
    fields = ['nome', 'descricao', 'preco']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Serviço', 'botao': 'Criar Serviço'}


class ServicoUpdate(UpdateView):
    model = Servico
    fields = ['nome', 'descricao', 'preco']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados do Serviço',
                     'botao': 'Atualizar Serviço'}


class ServicoDelete(DeleteView):
    model = Servico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Serviço', 'botao': 'Sim, excluir!'}


class ServicoList(ListView):
    model = Servico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Serviços'}


class ServicoDetail(DetailView):
    model = Servico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Serviço'}


# =========================
# Peca
# =========================
class PecaCreate(CreateView):
    model = Peca
    fields = ['nome', 'fabricante', 'codigo', 'descricao', 'preco', 'estoque']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Peça', 'botao': 'Criar Peça'}


class PecaUpdate(UpdateView):
    model = Peca
    fields = ['nome', 'fabricante', 'codigo', 'descricao', 'preco', 'estoque']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados da Peça',
                     'botao': 'Atualizar Peça'}


class PecaDelete(DeleteView):
    model = Peca
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Peça', 'botao': 'Sim, excluir!'}


class PecaList(ListView):
    model = Peca
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Peças'}


class PecaDetail(DetailView):
    model = Peca
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes da Peça'}


# =========================
# Funcionario
# =========================
class FuncionarioCreate(CreateView):
    model = Funcionario
    fields = ['nome', 'cpf', 'data_nascimento',
              'telefone', 'cargo', 'salario', 'horas_semanais']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Funcionário',
                     'botao': 'Criar Funcionário'}


class FuncionarioUpdate(UpdateView):
    model = Funcionario
    fields = ['nome', 'cpf', 'data_nascimento',
              'telefone', 'cargo', 'salario', 'horas_semanais']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados do Funcionário',
                     'botao': 'Atualizar Funcionário'}


class FuncionarioDelete(DeleteView):
    model = Funcionario
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Funcionário', 'botao': 'Sim, excluir!'}


class FuncionarioList(ListView):
    model = Funcionario
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Funcionários'}


class FuncionarioDetail(DetailView):
    model = Funcionario
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Funcionário'}


# =========================
# Mecanico
# =========================
class MecanicoCreate(CreateView):
    model = Mecanico
    fields = ['nome', 'cpf', 'data_nascimento', 'telefone',
              'cargo', 'salario', 'horas_semanais', 'especialidade']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Mecânico',
                     'botao': 'Criar Mecânico'}


class MecanicoUpdate(UpdateView):
    model = Mecanico
    fields = ['nome', 'cpf', 'data_nascimento', 'telefone',
              'cargo', 'salario', 'horas_semanais', 'especialidade']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados do Mecânico',
                     'botao': 'Atualizar Mecânico'}


class MecanicoDelete(DeleteView):
    model = Mecanico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Mecânico', 'botao': 'Sim, excluir!'}


class MecanicoList(ListView):
    model = Mecanico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Mecânicos'}


class MecanicoDetail(DetailView):
    model = Mecanico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Mecânico'}


# =========================
# ConsultorTecnico
# =========================
class ConsultorTecnicoCreate(CreateView):
    model = ConsultorTecnico
    fields = ['nome', 'cpf', 'data_nascimento',
              'telefone', 'cargo', 'salario', 'horas_semanais']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Consultor Técnico',
                     'botao': 'Criar Consultor Técnico'}


class ConsultorTecnicoUpdate(UpdateView):
    model = ConsultorTecnico
    fields = ['nome', 'cpf', 'data_nascimento',
              'telefone', 'cargo', 'salario', 'horas_semanais']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados do Consultor Técnico',
                     'botao': 'Atualizar Consultor Técnico'}


class ConsultorTecnicoDelete(DeleteView):
    model = ConsultorTecnico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Consultor Técnico',
                     'botao': 'Sim, excluir!'}


class ConsultorTecnicoList(ListView):
    model = ConsultorTecnico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Consultores Técnicos'}


class ConsultorTecnicoDetail(DetailView):
    model = ConsultorTecnico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes do Consultor Técnico'}


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
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Ordem de Serviço',
                     'botao': 'Criar Ordem de Serviço'}


class OrdemServicoUpdate(UpdateView):
    model = OrdemServico
    fields = [
        'estado', 'preco', 'previsao_termino', 'data_termino', 'descricao',
        'observacao', 'carro', 'consultorTecnico', 'mecanicos', 'servicos'
    ]
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados da Ordem de Serviço',
                     'botao': 'Atualizar Ordem de Serviço'}


class OrdemServicoDelete(DeleteView):
    model = OrdemServico
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Ordem de Serviço',
                     'botao': 'Sim, excluir!'}


class OrdemServicoList(ListView):
    model = OrdemServico
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Ordens de Serviço'}


class OrdemServicoDetail(DetailView):
    model = OrdemServico
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes da Ordem de Serviço'}


# =========================
# OrdemPecas
# =========================
class OrdemPecasCreate(CreateView):
    model = OrdemPecas
    fields = ['peca', 'ordem_servico', 'quantidade', 'preco']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Cadastro de Ordem de Peças',
                     'botao': 'Criar Ordem de Peças'}


class OrdemPecasUpdate(UpdateView):
    model = OrdemPecas
    fields = ['peca', 'ordem_servico', 'quantidade', 'preco']
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Editar dados da Ordem de Peças',
                     'botao': 'Atualizar Ordem de Peças'}


class OrdemPecasDelete(DeleteView):
    model = OrdemPecas
    template_name = 'mecanica/form.html'
    success_url = reverse_lazy('index')
    extra_context = {'titulo': 'Excluir Ordem de Peças',
                     'botao': 'Sim, excluir!'}


class OrdemPecasList(ListView):
    model = OrdemPecas
    template_name = 'mecanica/list.html'
    extra_context = {'titulo': 'Lista de Ordens de Peças'}


class OrdemPecasDetail(DetailView):
    model = OrdemPecas
    template_name = 'mecanica/detail.html'
    extra_context = {'titulo': 'Detalhes da Ordem de Peças'}


from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    nome = models.CharField(max_length=60)
    cpf = models.CharField(unique=True, max_length=11)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nome} - {self.data_nascimento} - {self.cpf}"
    
    class Meta:
        ordering = ['nome']


class Carro(models.Model):
    vin = models.CharField(max_length=17)
    placa = models.CharField(max_length=7)
    modelo = models.CharField(max_length=80)
    cor = models.CharField(max_length=20)
    ano = models.IntegerField()
    quilometragem = models.PositiveIntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.modelo} - {self.cor} - {self.placa}"
    
    class Meta:
        ordering = ['modelo']


class Servico(models.Model):
    nome = models.CharField(max_length=60)
    descricao = models.CharField(max_length=200, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nome}"
    
    class Meta:
        ordering = ['nome']


class Peca(models.Model):
    nome = models.CharField(max_length=40)
    fabricante = models.CharField(max_length=30)
    codigo = models.CharField(max_length=60)
    descricao = models.CharField(max_length=100, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nome} - {self.fabricante} - {self.codigo}"
    
    class Meta:
        ordering = ['nome']


class Funcionario(models.Model):
    nome = models.CharField(max_length=60)
    cpf = models.CharField(unique=True, max_length=11)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    cargo = models.CharField(max_length=40)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    horas_semanais = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nome} - {self.cargo} - {self.data_nascimento}"
    
    class Meta:
        ordering = ['nome']


class Mecanico(Funcionario):
    especialidade = models.CharField(max_length=40, null=True)

    def __str__(self):
        return f"{self.nome} - {self.especialidade}"
    
    class Meta:
        ordering = ['especialidade']


class ConsultorTecnico(Funcionario):
    def __str__(self):
        return f"{self.nome}"


class OrdemServico(models.Model):
    estado = models.CharField(max_length=20)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateTimeField(auto_now_add=True)
    previsao_termino = models.DateTimeField(null=True)
    data_termino = models.DateTimeField(null=True)
    descricao = models.CharField(max_length=100, null=True)
    observacao = models.CharField(max_length=200, null=True)
    carro = models.ForeignKey(Carro, on_delete=models.PROTECT)
    consultorTecnico = models.ForeignKey(
        ConsultorTecnico, on_delete=models.PROTECT)
    mecanicos = models.ManyToManyField(Mecanico)
    servicos = models.ManyToManyField(Servico)

    def __str__(self):
        return f"{self.carro.modelo} - {self.carro.cor} - {self.estado} - {self.data_inicio}"
    
    class Meta:
        verbose_name_plural = "OrdensServico"
        ordering = ['-data_inicio']


class OrdemPecas(models.Model):
    peca = models.ForeignKey(Peca, on_delete=models.PROTECT)
    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"({self.peca.nome} - {self.ordem_servico.carro.vin} - {self.quantidade})"
    
    class Meta:
        verbose_name_plural = "OrdensPecas"
        ordering = ['ordem_servico']

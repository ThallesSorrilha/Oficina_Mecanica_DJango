from django import forms

from .models import OrdemPecas, OrdemServico, OrdemServicoServico, Servico


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={"type": "date"})
            if isinstance(field, forms.DateTimeField):
                field.widget = forms.DateTimeInput(
                    attrs={"type": "datetime-local"})
            if isinstance(field, forms.ModelMultipleChoiceField):
                field.help_text = "- Segure a tecla 'Ctrl' para selecionar mais de um item -"


class OrdemPecasForm(BaseModelForm):
    class Meta:
        model = OrdemPecas
        fields = ['peca', 'ordem_servico', 'quantidade']

    def save(self, commit=True):
        item = super().save(commit=False)
        item.preco_unitario = item.peca.preco
        if commit:
            item.save()
        return item


class OrdemServicoForm(BaseModelForm):
    servicos = forms.ModelMultipleChoiceField(
        queryset=Servico.objects.all(),
        required=False,
    )

    class Meta:
        model = OrdemServico
        fields = [
            'estado', 'previsao_termino', 'data_termino', 'descricao',
            'observacao', 'carro', 'consultor_tecnico', 'mecanicos',
            'servicos',
        ]

    def save(self, commit=True):
        ordem = super().save(commit=False)
        if commit:
            ordem.save()
            ordem.mecanicos.set(self.cleaned_data['mecanicos'])
            OrdemServicoServico.objects.filter(ordem_servico=ordem).delete()
            OrdemServicoServico.objects.bulk_create([
                OrdemServicoServico(
                    ordem_servico=ordem,
                    servico=servico,
                    preco_unitario=servico.preco,
                )
                for servico in self.cleaned_data['servicos']
            ])
        return ordem


class OrdemServicoServicoForm(BaseModelForm):
    class Meta:
        model = OrdemServicoServico
        fields = ['servico', 'ordem_servico']

    def save(self, commit=True):
        item = super().save(commit=False)
        item.preco_unitario = item.servico.preco
        if commit:
            item.save()
        return item

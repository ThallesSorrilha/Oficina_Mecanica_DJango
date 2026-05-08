from django import forms


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={"type": "date"})
            if isinstance(field, forms.DateTimeField):
                field.widget = forms.DateTimeInput(attrs={"type": "datetime-local"})
            if isinstance(field, forms.ModelMultipleChoiceField):
                field.help_text = "- Segure a tecla 'Ctrl' para selecionar mais de um item -"

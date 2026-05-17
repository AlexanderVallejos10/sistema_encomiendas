from django import forms
from .models import Encomienda
from clientes.models import Cliente
from rutas.models import Ruta
from my_project.choices import EstadoGeneral


class EncomiendaForm(forms.ModelForm):
    class Meta:
        model = Encomienda
        fields = [
            'descripcion',
            'peso_kg',
            'remitente',
            'destinatario',
            'ruta',
            'fecha_entrega_est',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'required': True,
                'placeholder': 'Descripción de la encomienda'
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'remitente': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'destinatario': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'ruta': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'fecha_entrega_est': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['remitente'].queryset = Cliente.objects.filter(
            estado=EstadoGeneral.ACTIVO
        )

        self.fields['destinatario'].queryset = Cliente.objects.filter(
            estado=EstadoGeneral.ACTIVO
        )

        self.fields['ruta'].queryset = Ruta.objects.filter(
            estado=EstadoGeneral.ACTIVO
        )

    def clean(self):
        cleaned_data = super().clean()
        remitente = cleaned_data.get('remitente')
        destinatario = cleaned_data.get('destinatario')

        if remitente and destinatario and remitente == destinatario:
            self.add_error(
                'destinatario',
                'El destinatario no puede ser el mismo que el remitente.'
            )

        return cleaned_data
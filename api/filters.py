from django_filters.rest_framework import FilterSet, CharFilter, ChoiceFilter

from envios.models import Encomienda


ESTADOS_ENCOMIENDA = [
    ('PE', 'Pendiente'),
    ('TR', 'En tránsito'),
    ('DE', 'En destino'),
    ('EN', 'Entregado'),
    ('DV', 'Devuelto'),
]


class EncomiendaFilter(FilterSet):
    estado = ChoiceFilter(choices=ESTADOS_ENCOMIENDA)
    ruta = CharFilter(field_name='ruta__codigo', lookup_expr='iexact')
    remitente = CharFilter(field_name='remitente__nro_doc')
    desde = CharFilter(field_name='fecha_registro__date', lookup_expr='gte')
    hasta = CharFilter(field_name='fecha_registro__date', lookup_expr='lte')
    con_retraso = CharFilter(method='filter_retraso')

    def filter_retraso(self, queryset, name, value):
        if value and value.lower() == 'true':
            return queryset.con_retraso()
        return queryset

    class Meta:
        model = Encomienda
        fields = [
            'estado',
            'ruta',
            'remitente',
            'desde',
            'hasta',
        ]
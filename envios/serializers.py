from rest_framework import serializers

from .models import Encomienda, HistorialEstado, Empleado
from clientes.models import Cliente
from rutas.models import Ruta


# ─────────────────────────────────────────────
# Cliente
# ─────────────────────────────────────────────
class ClienteSerializer(serializers.ModelSerializer):

    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo_doc',
            'nro_doc',
            'nombres',
            'apellidos',
            'nombre_completo',
            'telefono',
            'email',
            'direccion',
            'estado',
        ]


# ─────────────────────────────────────────────
# Ruta
# ─────────────────────────────────────────────
class RutaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ruta
        fields = [
            'id',
            'codigo',
            'origen',
            'destino',
            'precio_base',
            'dias_entrega',
            'estado',
        ]


# ─────────────────────────────────────────────
# Historial Estado
# ─────────────────────────────────────────────
class HistorialEstadoSerializer(serializers.ModelSerializer):

    empleado_nombre = serializers.StringRelatedField(
        source='empleado',
        read_only=True
    )

    estado_anterior_display = serializers.CharField(
        source='get_estado_anterior_display',
        read_only=True
    )

    estado_nuevo_display = serializers.CharField(
        source='get_estado_nuevo_display',
        read_only=True
    )

    class Meta:
        model = HistorialEstado
        fields = [
            'id',
            'estado_anterior',
            'estado_anterior_display',
            'estado_nuevo',
            'estado_nuevo_display',
            'empleado_nombre',
            'observacion',
            'fecha_cambio',
        ]


# ─────────────────────────────────────────────
# Encomienda
# ─────────────────────────────────────────────
class EncomiendaSerializer(serializers.ModelSerializer):

    estado_display = serializers.SerializerMethodField()

    tiene_retraso = serializers.ReadOnlyField()
    dias_en_transito = serializers.ReadOnlyField()
    esta_entregada = serializers.ReadOnlyField()

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'descripcion',
            'peso_kg',
            'costo_envio',

            'remitente',
            'destinatario',
            'ruta',
            'empleado_registro',

            'estado',
            'estado_display',

            'fecha_registro',
            'fecha_entrega_est',
            'fecha_entrega_real',

            'tiene_retraso',
            'dias_en_transito',
            'esta_entregada',
        ]

        read_only_fields = [
            'codigo',
            'costo_envio',
            'empleado_registro',
            'estado',
            'fecha_registro',
            'fecha_entrega_real',
        ]

    def get_estado_display(self, obj):
        return obj.get_estado_display()


# ─────────────────────────────────────────────
# Detalle completo
# ─────────────────────────────────────────────
class EncomiendaDetailSerializer(EncomiendaSerializer):

    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)

    historial = HistorialEstadoSerializer(
        many=True,
        read_only=True
    )

    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.filter(estado=1),
        source='remitente',
        write_only=True
    )

    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.filter(estado=1),
        source='destinatario',
        write_only=True
    )

    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.filter(estado=1),
        source='ruta',
        write_only=True
    )

    class Meta(EncomiendaSerializer.Meta):
        fields = EncomiendaSerializer.Meta.fields + [
            'historial',
            'remitente_id',
            'destinatario_id',
            'ruta_id',
        ]

class EncomiendaV2Serializer(serializers.ModelSerializer):
    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)

    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.filter(estado=1),
        source='remitente',
        write_only=True
    )

    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.filter(estado=1),
        source='destinatario',
        write_only=True
    )

    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.filter(estado=1),
        source='ruta',
        write_only=True
    )

    estado_display = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()

    tiene_retraso = serializers.ReadOnlyField()
    dias_en_transito = serializers.ReadOnlyField()
    esta_entregada = serializers.ReadOnlyField()

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'descripcion',
            'peso_kg',
            'costo_envio',

            'remitente',
            'remitente_id',
            'destinatario',
            'destinatario_id',
            'ruta',
            'ruta_id',

            'empleado_registro',
            'estado',
            'estado_display',

            'fecha_registro',
            'fecha_entrega_est',
            'fecha_entrega_real',

            'tiene_retraso',
            'dias_en_transito',
            'esta_entregada',
            'meta',
        ]

        read_only_fields = [
            'codigo',
            'costo_envio',
            'empleado_registro',
            'estado',
            'fecha_registro',
            'fecha_entrega_real',
        ]

    def get_estado_display(self, obj):
        return obj.get_estado_display()

    def get_meta(self, obj):
        from django.utils import timezone

        return {
            'version': 'v2',
            'generado': timezone.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'puede_editar': not obj.esta_entregada,
        }
import uuid

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import EncomiendaFilter
from api.pagination import EncomiendaPagination, ClientePagination, HistorialPagination
from api.permissions import EsEmpleadoActivo, EsPropietarioOAdmin
from api.throttles import EmpleadoRateThrottle, CambioEstadoThrottle
from clientes.models import Cliente
from rutas.models import Ruta
from my_project.choices import EstadoEnvio

from .models import Encomienda, Empleado
from .serializers import (
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
    HistorialEstadoSerializer,
    ClienteSerializer,
    EncomiendaV2Serializer,
    RutaSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary='Listar encomiendas',
        description='Devuelve la lista paginada de encomiendas con filtros, búsqueda y ordenamiento.',
        tags=['Encomiendas'],
    ),
    create=extend_schema(
        summary='Crear encomienda',
        description='Registra una nueva encomienda. El código, costo, estado y empleado se asignan automáticamente.',
        tags=['Encomiendas'],
    ),
    retrieve=extend_schema(
        summary='Detalle de encomienda',
        description='Devuelve la información completa de una encomienda.',
        tags=['Encomiendas'],
    ),
    update=extend_schema(summary='Actualizar encomienda', tags=['Encomiendas']),
    partial_update=extend_schema(summary='Actualizar encomienda parcialmente', tags=['Encomiendas']),
    destroy=extend_schema(summary='Eliminar encomienda', tags=['Encomiendas']),
)
class EncomiendaViewSet(viewsets.ModelViewSet):
    permission_classes = [EsEmpleadoActivo]
    pagination_class = EncomiendaPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EncomiendaFilter
    throttle_classes = [EmpleadoRateThrottle]

    search_fields = [
        'codigo',
        'descripcion',
        'remitente__nombres',
        'remitente__apellidos',
        'destinatario__nombres',
        'destinatario__apellidos',
        'ruta__origen',
        'ruta__destino',
    ]

    ordering_fields = [
        'fecha_registro',
        'peso_kg',
        'costo_envio',
    ]

    ordering = ['-fecha_registro']

    def get_queryset(self):
        return Encomienda.objects.all().select_related(
            'remitente',
            'destinatario',
            'ruta',
            'empleado_registro',
        )

    def get_throttles(self):
        if self.action == 'cambiar_estado':
            return [CambioEstadoThrottle()]
        return super().get_throttles()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [EsEmpleadoActivo(), EsPropietarioOAdmin()]
        return [EsEmpleadoActivo()]

    def get_serializer_class(self):
        version = getattr(self.request, 'version', 'v1')

        if version == 'v2':
            return EncomiendaV2Serializer

        if self.action == 'retrieve':
            return EncomiendaDetailSerializer

        return EncomiendaSerializer

    def perform_create(self, serializer):
        empleado = Empleado.objects.get(email=self.request.user.email)

        codigo = f'ENC-{timezone.now().strftime("%Y%m%d")}-{str(uuid.uuid4())[:6].upper()}'

        encomienda = serializer.save(
            codigo=codigo,
            empleado_registro=empleado,
            estado=EstadoEnvio.PENDIENTE,
            costo_envio=0,
        )

        encomienda.costo_envio = encomienda.calcular_costo()
        encomienda.save()

    @extend_schema(
        summary='Cambiar estado de encomienda',
        description='Cambia el estado de una encomienda y registra el cambio en el historial.',
        request=OpenApiTypes.OBJECT,
        responses={
            200: EncomiendaSerializer,
            400: OpenApiResponse(description='Estado inválido o error de validación'),
        },
        examples=[
            OpenApiExample(
                'Pasar a En tránsito',
                value={
                    'estado': 'TR',
                    'observacion': 'Salida de almacén',
                },
                request_only=True,
            )
        ],
        tags=['Encomiendas'],
    )
    @action(detail=True, methods=['post'], url_path='cambiar_estado')
    def cambiar_estado(self, request, pk=None, version=None, *args, **kwargs):
        encomienda = self.get_object()

        nuevo_estado = request.data.get('estado')
        observacion = request.data.get('observacion', '')

        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado es requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            empleado = Empleado.objects.get(email=self.request.user.email)

            encomienda.cambiar_estado(
                nuevo_estado,
                empleado,
                observacion,
            )

            serializer = self.get_serializer(encomienda)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Empleado.DoesNotExist:
            return Response(
                {'error': 'No existe un empleado asociado a este usuario.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary='Encomiendas con retraso',
        description='Lista las encomiendas activas cuya fecha estimada de entrega ya pasó.',
        tags=['Encomiendas'],
    )
    @action(detail=False, methods=['get'], url_path='con_retraso')
    def con_retraso(self, request, version=None, *args, **kwargs):
        qs = Encomienda.objects.con_retraso().select_related(
            'remitente',
            'destinatario',
            'ruta',
            'empleado_registro',
        )

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Encomiendas pendientes',
        description='Lista todas las encomiendas en estado Pendiente.',
        tags=['Encomiendas'],
    )
    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request, version=None, *args, **kwargs):
        qs = Encomienda.objects.pendientes().select_related(
            'remitente',
            'destinatario',
            'ruta',
            'empleado_registro',
        )

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Historial de estados',
        description='Devuelve el historial paginado de cambios de estado de una encomienda.',
        tags=['Encomiendas'],
    )
    @action(detail=True, methods=['get'], url_path='historial')
    def historial(self, request, pk=None, version=None, *args, **kwargs):
        encomienda = self.get_object()

        qs = encomienda.historial.select_related('empleado').order_by('-fecha_cambio')

        paginator = HistorialPagination()
        page = paginator.paginate_queryset(qs, request)

        if page is not None:
            serializer = HistorialEstadoSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = HistorialEstadoSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Estadísticas globales',
        description='Devuelve contadores globales del sistema.',
        tags=['Encomiendas'],
    )
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request, version=None, *args, **kwargs):
        hoy = timezone.now().date()

        return Response({
            'total_activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.filter(
                estado=EstadoEnvio.EN_TRANSITO
            ).count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(
                estado=EstadoEnvio.ENTREGADO,
                fecha_entrega_real=hoy,
            ).count(),
        })


class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientePagination
    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        'nro_doc',
        'nombres',
        'apellidos',
        'email',
    ]

    ordering_fields = [
        'apellidos',
        'nombres',
        'fecha_registro',
    ]

    ordering = ['apellidos', 'nombres']

    def get_queryset(self):
        return Cliente.objects.filter(estado=1)


class RutaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        'codigo',
        'origen',
        'destino',
    ]

    ordering_fields = [
        'origen',
        'destino',
        'precio_base',
        'dias_entrega',
    ]

    ordering = ['origen', 'destino']

    def get_queryset(self):
        return Ruta.objects.filter(estado=1)
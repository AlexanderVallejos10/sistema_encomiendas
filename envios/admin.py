from django.contrib import admin
from django.utils.html import format_html
from .models import Empleado, Encomienda, HistorialEstado


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'remitente',
        'destinatario',
        'ruta',
        'estado_badge',
        'peso_kg',
        'costo_envio',
        'fecha_registro',
    )

    list_filter = ('estado', 'ruta', 'fecha_registro')
    search_fields = (
        'codigo',
        'remitente__nro_doc',
        'remitente__nombres',
        'remitente__apellidos',
        'destinatario__nro_doc',
        'destinatario__nombres',
        'destinatario__apellidos',
    )

    readonly_fields = ('fecha_registro', 'fecha_entrega_real')

    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'descripcion', 'peso_kg', 'costo_envio')
        }),
        ('Personas relacionadas', {
            'fields': ('remitente', 'destinatario', 'empleado_registro')
        }),
        ('Ruta y estado', {
            'fields': ('ruta', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'fecha_entrega_est', 'fecha_entrega_real')
        }),
    )

    def estado_badge(self, obj):
        colores = {
            'PE': '#6c757d',
            'TR': '#0d6efd',
            'DE': '#fd7e14',
            'EN': '#198754',
            'DV': '#dc3545',
        }

        color = colores.get(obj.estado, '#6c757d')

        return format_html(
            '<span style="background:{}; color:white; padding:4px 10px; border-radius:12px; font-weight:bold;">{}</span>',
            color,
            obj.get_estado_display()
        )

    estado_badge.short_description = 'Estado'


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'apellidos', 'nombres', 'cargo', 'email', 'estado')
    list_filter = ('estado', 'cargo')
    search_fields = ('codigo', 'apellidos', 'nombres', 'email')

    fieldsets = (
        ('Datos personales', {
            'fields': ('codigo', 'nombres', 'apellidos')
        }),
        ('Información laboral', {
            'fields': ('cargo', 'email', 'telefono', 'fecha_ingreso', 'estado')
        }),
    )


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = (
        'encomienda',
        'estado_anterior',
        'estado_nuevo',
        'empleado',
        'fecha_cambio',
    )
    list_filter = ('estado_anterior', 'estado_nuevo', 'fecha_cambio')
    search_fields = ('encomienda__codigo', 'empleado__nombres', 'empleado__apellidos')
    readonly_fields = ('fecha_cambio',)

    fieldsets = (
        ('Cambio de estado', {
            'fields': ('encomienda', 'estado_anterior', 'estado_nuevo')
        }),
        ('Responsable y observación', {
            'fields': ('empleado', 'observacion', 'fecha_cambio')
        }),
    )
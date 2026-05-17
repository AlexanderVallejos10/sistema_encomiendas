from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.utils import timezone
import uuid
from .models import Encomienda, Empleado
from my_project.choices import EstadoEnvio


@login_required
def dashboard(request):
    hoy = timezone.now().date()

    context = {
        'total_activas': Encomienda.objects.activas().count(),
        'en_transito': Encomienda.objects.filter(estado=EstadoEnvio.EN_TRANSITO).count(),
        'con_retraso': Encomienda.objects.con_retraso().count(),
        'entregadas_hoy': Encomienda.objects.filter(
            estado=EstadoEnvio.ENTREGADO,
            fecha_entrega_real=hoy
        ).count(),
        'ultimas': Encomienda.objects.select_related(
            'remitente', 'destinatario', 'ruta', 'empleado_registro'
        ).order_by('-fecha_registro')[:5],
    }

    return render(request, 'envios/dashboard.html', context)


@login_required
def encomienda_lista(request):
    qs = Encomienda.objects.select_related(
        'remitente', 'destinatario', 'ruta', 'empleado_registro'
    ).order_by('-fecha_registro')

    estado = request.GET.get('estado', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)

    if q:
        qs = qs.filter(
            Q(codigo__icontains=q) |
            Q(remitente__nombres__icontains=q) |
            Q(remitente__apellidos__icontains=q) |
            Q(destinatario__nombres__icontains=q) |
            Q(destinatario__apellidos__icontains=q)
        )

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    encomiendas = paginator.get_page(page_number)

    return render(request, 'envios/lista.html', {
        'encomiendas': encomiendas,
        'estados': EstadoEnvio.choices,
        'estado_activo': estado,
    })


@login_required
def encomienda_detalle(request, pk):
    encomienda = get_object_or_404(
        Encomienda.objects.select_related(
            'remitente', 'destinatario', 'ruta', 'empleado_registro'
        ),
        pk=pk
    )

    historial = encomienda.historial.select_related('empleado').all()

    return render(request, 'envios/detalle.html', {
        'encomienda': encomienda,
        'historial': historial,
        'estados': EstadoEnvio.choices,
    })


@login_required
def encomienda_crear(request):
    from .forms import EncomiendaForm

    if request.method == 'POST':
        form = EncomiendaForm(request.POST)

        if form.is_valid():
            enc = form.save(commit=False)

            try:
                empleado = Empleado.objects.get(email=request.user.email)
            except Empleado.DoesNotExist:
                messages.error(request, 'No existe un empleado asociado a este usuario.')
                return redirect('encomienda_lista')

            enc.empleado_registro = empleado
            enc.codigo = f'ENC-{timezone.now().strftime("%Y%m%d")}-{str(uuid.uuid4())[:6].upper()}'
            enc.costo_envio = enc.calcular_costo()
            enc.save()

            messages.success(request, f'Encomienda {enc.codigo} registrada correctamente.')
            return redirect('encomienda_detalle', pk=enc.pk)

    else:
        form = EncomiendaForm()

    return render(request, 'envios/form.html', {
        'form': form,
        'titulo': 'Nueva Encomienda',
    })


@require_POST
@login_required
def encomienda_cambiar_estado(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)
    nuevo_estado = request.POST.get('estado')
    observacion = request.POST.get('observacion', '')

    try:
        empleado = Empleado.objects.get(email=request.user.email)
        encomienda.cambiar_estado(nuevo_estado, empleado, observacion)
        messages.success(request, 'Estado actualizado correctamente.')
    except Empleado.DoesNotExist:
        messages.error(request, 'No existe un empleado asociado a este usuario.')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('encomienda_detalle', pk=pk)



@login_required
def encomienda_editar(request, pk):
    from .forms import EncomiendaForm

    encomienda = get_object_or_404(Encomienda, pk=pk)

    if request.method == 'POST':
        form = EncomiendaForm(request.POST, instance=encomienda)

        if form.is_valid():
            enc = form.save(commit=False)
            enc.costo_envio = enc.calcular_costo()
            enc.save()

            messages.success(request, f'Encomienda {enc.codigo} actualizada correctamente.')
            return redirect('encomienda_detalle', pk=enc.pk)
    else:
        form = EncomiendaForm(instance=encomienda)

    return render(request, 'envios/form.html', {
        'form': form,
        'titulo': f'Editar Encomienda {encomienda.codigo}',
    })


@login_required
def encomienda_eliminar(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)

    if request.method == 'POST':
        codigo = encomienda.codigo
        encomienda.delete()
        messages.success(request, f'Encomienda {codigo} eliminada correctamente.')
        return redirect('encomienda_lista')

    return render(request, 'envios/confirmar_eliminar.html', {
        'encomienda': encomienda,
    })





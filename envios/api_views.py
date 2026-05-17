from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Encomienda
from .serializers import (
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
)


# ─────────────────────────────────────────────
# LISTAR Y CREAR
# ─────────────────────────────────────────────
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def encomienda_list(request):

    # GET → listar
    if request.method == 'GET':

        qs = Encomienda.objects.all()

        serializer = EncomiendaSerializer(
            qs,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    # POST → crear
    elif request.method == 'POST':

        serializer = EncomiendaSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# ─────────────────────────────────────────────
# DETALLE / ACTUALIZAR / ELIMINAR
# ─────────────────────────────────────────────
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def encomienda_detail(request, pk):

    enc = get_object_or_404(
        Encomienda,
        pk=pk
    )

    # GET → detalle
    if request.method == 'GET':

        serializer = EncomiendaDetailSerializer(enc)

        return Response(serializer.data)

    # PUT / PATCH → actualizar
    elif request.method in ['PUT', 'PATCH']:

        serializer = EncomiendaSerializer(
            enc,
            data=request.data,
            partial=(request.method == 'PATCH')
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # DELETE → eliminar
    elif request.method == 'DELETE':

        enc.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
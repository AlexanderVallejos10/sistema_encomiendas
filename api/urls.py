from django.urls import path, include
from rest_framework.routers import DefaultRouter
from envios.viewsets import EncomiendaViewSet, ClienteViewSet, RutaViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from envios.viewsets import EncomiendaViewSet


router = DefaultRouter()

router.register('encomiendas', EncomiendaViewSet, basename='encomienda')
router.register('clientes', ClienteViewSet, basename='cliente')
router.register('rutas', RutaViewSet, basename='ruta')


urlpatterns = [

    # JWT
    path(
        'auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain'
    ),

    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    # Swagger
    path(
        'schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),

    path(
        'docs/',
        SpectacularSwaggerView.as_view(
            url_name='schema'
        ),
        name='swagger'
    ),

    path('', include(router.urls)),
]
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


# PERSONALIZACIÓN DEL PANEL ADMIN
admin.site.site_header = "Sistema de Encomiendas"
admin.site.site_title = "Panel Administrativo"
admin.site.index_title = "Administración"

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    # App envios
    path('', include('envios.urls')),
    path('api/<version>/', include('api.urls')),
    ]


# Archivos estáticos y media en DEBUG
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
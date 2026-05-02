from django.urls import path
from . import views
from .views_auth import login_view, logout_view, perfil_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil_view, name='perfil'),
    path('', views.dashboard, name='dashboard'),
    path('encomiendas/', views.encomienda_lista, name='encomienda_lista'),
    path('encomiendas/nueva/', views.encomienda_crear, name='encomienda_crear'),
    path('encomiendas/<int:pk>/', views.encomienda_detalle, name='encomienda_detalle'),
    path('encomiendas/<int:pk>/estado/', views.encomienda_cambiar_estado, name='encomienda_cambiar_estado'),
    path('encomiendas/<int:pk>/editar/', views.encomienda_editar, name='encomienda_editar'),
    path('encomiendas/<int:pk>/eliminar/', views.encomienda_eliminar, name='encomienda_eliminar'),
]
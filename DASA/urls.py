from django.urls import path
from DASA import views

urlpatterns = [
    path('', views.inicioUsuario, name = "inicio_usuario"),
    path('cambiar-contraseña/', views.cambiar_contraseña, name='cambiar_contraseña'),
    # planillas
    path('planillas/editar_aspectos/<int:id_planilla>', views.editar_aspectos_planilla, name='editar_aspectos_planilla'), 
    path('planillas/añadir_informacion/<int:id_planilla>', views.añadir_informacion_planilla, name='añadir_informacion_planilla'), 
    path('planillas/añadir_planilla/<int:obra>', views.añadir_planilla, name='añadir_planilla'), 
    path('visitas/', views.visitas, name='visitas'),
    path('planillas/editar_planilla/<int:id_planilla>', views.editar_planilla, name='editar_planilla'),
    path('planillas/detalle_planilla/<int:id_planilla>', views.detalle_planilla, name='detalle_planilla'), 
    # obras
    path('obras/añadir_obra', views.añadir_obra, name='añadir_obra'),
    path('obras/detalle_obra/<int:id_obra>', views.detalle_obra, name='detalle_obra'),
    path('obras/editar_obra/<int:id_obra>', views.editar_obra, name='editar_obra'),
    path('obras/eliminar_obra/<int:id_obra>', views.eliminar_obra, name='eliminar_obra'),
    path('obras/', views.lista_obra, name='lista_obra'),
    # empresa
    path('empresas/añadir_empresa', views.añadir_empresa, name='añadir_empresa'),
    path('empresas/detalle_empresa/<int:id_empresa>', views.detalle_empresa, name='detalle_empresa'), 
    path('empresas/editar_empresa/<int:id_empresa>', views.editar_empresa, name='editar_empresa'), 
    path('empresas/eliminar_empresa/<int:id_empresa>', views.eliminar_empresa, name='eliminar_empresa'), 
    path('empresas/', views.lista_empresa, name='lista_empresa'),
    # regulacion
    path('regulacion/editar_documento/<int:id_doc>', views.editar_documentos_obra, name='editar_documento'),
    path('regulacion/añadir_documento/<int:id_obra>', views.añadir_documentos_obra, name='añadir_documento'),
    # art
    path('ART/', views.lista_ART, name='lista_ART'),
    path('ART/agregar/', views.añadir_ART, name='añadir_ART'),
    path('ART/editar/<int:id_ART>', views.editar_ART, name='editar_ART'),
    path('ART/eliminar/<int:id_ART>', views.eliminar_ART, name='eliminar_ART'),

    # licenciado
    path('licenciados/', views.lista_licenciado, name='lista_licenciado'),
    path('licenciados/agregar/', views.añadir_licenciado, name='añadir_licenciado'),
    path('licenciados/detalle/<int:id_licenciado>', views.detalle_licenciado, name='detalle_licenciado'), 
    path('licenciados/editar/<int:id_licenciado>', views.editar_licenciado, name='editar_licenciado'), 
    path('licenciados/eliminar/<int:id_licenciado>', views.eliminar_licenciado, name='eliminar_licenciado'), 

    #nomina
    path('nomina/agregar/<int:obra>', views.añadir_nomina, name='añadir_nomina'),
    # path('nomina/detalle/<int:id_persona>', views.detalle_nomina, name='detalle_nomina'), 
    path('nomina/editar/<int:id_persona>', views.editar_nomina, name='editar_nomina'), 
    path('nomina/eliminar/<int:id_persona>', views.eliminar_nomina, name='eliminar_nomina'), 

]
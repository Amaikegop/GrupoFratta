from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from DASA.middleware import get_current_user
from .models import Planilla, AspectoSeguridad, Empresa, ResponsableObra, Obra, DocumentoObra, HistorialPlanilla
from DASA.utils import enviar_mail_planilla
@receiver(post_save, sender=Planilla)
def agregar_info_planilla(sender, instance, created, **kwargs):
    if created:
        # Crear los Aspectos de Seguridad asociados
        for tipo, _ in AspectoSeguridad.TipoAspecto.choices:
            AspectoSeguridad.objects.create(planilla=instance, tipo=tipo)

@receiver(post_delete, sender=Empresa)
def eliminar_usuario_empresa(sender, instance, **kwargs):
    user = User.objects.filter(id = instance.usuario.id)
    user.delete()

@receiver(post_delete, sender=ResponsableObra)
def eliminar_usuario_licenciado(sender, instance, **kwargs):
    user = User.objects.filter(id = instance.usuario.id)
    user.delete()

@receiver(post_save, sender=Obra)
def agregar_info_obra(sender, instance, created, **kwargs):
    if created:
        sector = instance.sector

        # Documentos según sector
        if sector == 'AGRO':
            tipos_documentos = ['MEDICION_PAT', 'MEDICION_RUIDOS', 'MEDICION_ILUMINACION', 'ERGONOMIA', 'RGRL', 'RAR', 'CAPACITACION' ,'SIMULACRO', 'EPP', 'MATAFUEGOS', 'HABITABILIDAD', 'MAQUINARIAS', 'MATERIAL_PARTICULADO', 'HOJAS_SEGURIDAD']
        elif sector == 'CONSTRUCCION':
            tipos_documentos = ['PLANO', 'EST_DE SUELOS', 'AVISO_DE_OBRA', 'PROGRAMA', 'MEDICION_PAT', 'MEDICION_RUIDOS', 'MEDICION_ILUMINACION', 'ERGONOMIA', 'RGRL', 'RAR', 'CAPACITACION','SIMULACRO', 'EPP', 'MATAFUEGOS', 'BALANCIN']
        else: #industria y comercio
            tipos_documentos = ['MEDICION_PAT', 'MEDICION_RUIDOS', 'MEDICION_ILUMINACION', 'ERGONOMIA', 'RGRL', 'RAR', 'CAPACITACION','SIMULACRO', 'EPP', 'MATAFUEGOS', 'INFORME_TECNICO', 'AUTO_ELEVADOR', 'MATERIAL_PARTICULADO', 'HOJAS_SEGURIDAD', 'EVACUACION']


        for orden, tipo in enumerate(tipos_documentos):
            DocumentoObra.objects.create(obra=instance, tipo=tipo, orden= orden)



@receiver(post_save, sender=ResponsableObra)
def asignar_grupo_licenciado(sender, instance, created, **kwargs):
    if created:
        # Buscar al usuario por su CUIL
        nuevo_usuario = User.objects.filter(username=instance.CUIL).first()

        if nuevo_usuario:  # Verificar si el usuario existe
            grupo, _ = Group.objects.get_or_create(name='Licenciados')  # Obtener o crear el grupo
            nuevo_usuario.groups.add(grupo)  # Asignar grupo al usuario

@receiver(post_save, sender=Empresa)
def asignar_grupo_empresa(sender, instance, created, **kwargs):
    if created:
        # Buscar al usuario por su CUIL
        nuevo_usuario = User.objects.filter(username=instance.CUIT).first()

        if nuevo_usuario:  # Verificar si el usuario existe
            grupo, _ = Group.objects.get_or_create(name='Empresas')  # Obtener o crear el grupo
            nuevo_usuario.groups.add(grupo)  # Asignar grupo al usuario

@receiver(post_delete, sender=AspectoSeguridad)
def borrar_archivo_aspecto(sender, instance, **kwargs):
    if instance.imagen:
        instance.imagen.delete(False)

@receiver(post_delete, sender=HistorialPlanilla)
def borrar_archivo_historial(sender, instance, **kwargs):
    if instance.archivo:
        instance.archivo.delete(False)
    

@receiver(post_save, sender=HistorialPlanilla)
def enviar_mail(sender, instance, **kwargs):
    enviar_mail_planilla(instance)


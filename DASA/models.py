from xml.dom import ValidationErr
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator
from django import forms
from datetime import date
from django.db.models import Sum, Max
from django.core.files.base import ContentFile
from io import BytesIO
from DASA.utils import generar_pdf_buffer
from django.core.exceptions import ObjectDoesNotExist
import os

# Create your models here.

class ResponsableObra(models.Model):
    CUIL = models.CharField(primary_key=True, validators= [RegexValidator(
                regex=r'[0-9]{11}$',
                message="Formato de CUIL incorrecto."
    )])
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name}"

class ART(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.nombre}"
    
class Empresa(models.Model):
    CUIT = models.CharField(max_length=11, primary_key=True, validators=[RegexValidator(
                regex=r'[0-9]{11}$',  
                message="Formato de CUIT incorrecto."
            )])
    cel = models.CharField(null=True, blank=True,validators=[RegexValidator(
                regex=r'[0-9]$',  
                message="Solo números"
            )])
    usuario = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.usuario.first_name}"
    
    def vencimientos_de_obras(self):
        return len(self.obras_con_documentos_a_vencer()) > 0
    
    def obras_con_documentos_a_vencer(self):
        obras = self.obras.all()
        obras_a_vencer = []

        for obra in obras:
            if obra.documentos_a_vencer():
                obras_a_vencer.append(obra)
        
        return obras_a_vencer


    def documentos_faltantes_de_obras(self): #Devulve si hay o no doc faltantes
        return len(self.obras_con_documentos_faltantes()) > 0
    
    def obras_con_documentos_faltantes(self): #Devulve las obras
        obras = self.obras.all()
        obras_con_faltantes = []

        for obra in obras:
            if not obra.documentos.exists() or not obra.documentos_cargados():
                obras_con_faltantes.append(obra)
        
        return obras_con_faltantes

    def obras_con_visitas_riesgosas(self):
        return [obra for obra in self.obras.all() if obra.estado_incumplimiento()]

    def visitas_riesgosas_obras(self):
        return len(self.obras_con_visitas_riesgosas()) > 0

   
    def nuevas_visitas_semanales(self):
        return any(obra.generar_nueva_planilla() for obra in self.obras.all())
    
class Obra(models.Model):
    class Tipo(models.TextChoices):
        OBRA = "CONSTRUCCION", "Construcción"
        AGRO = "AGRO", "Agro"
        INDUSTRIA_COMERCIO  = "INDUSTRIA_COMERCIO", "Industria y comercio"
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="obras")
    dir_calle = models.CharField(max_length=50)
    dir_altura = models.CharField(max_length=5, validators=[RegexValidator(
                regex=r'[0-9]+$',
                message="Solo se admiten números"
    )])
    sector = models.CharField(choices=Tipo, null=True, max_length=20, )
    art = models.ForeignKey(to=ART, verbose_name='ART', null=True, on_delete=models.SET_NULL, related_name='obras')
    firma = models.ForeignKey(ResponsableObra, null=True, on_delete=models.SET_NULL, related_name="obras")

    def __str__(self):
        return f"Obra: {self.dir_calle} {self.dir_altura} - {self.empresa}"
    
    def direccion(self):
        return f"{self.dir_calle} {self.dir_altura}"

    #devulve si alguna planilla incumple
    def estado_incumplimiento(self):
        planillas = Planilla.objects.filter(obra=self, completa =True)
        
        planillas = [p for p in planillas if p.estado_incumplimiento()]
        
        if planillas:
            return True
        
        return False
    
    def planilla_estado_incumplimiento(self):
        planillas = Planilla.objects.filter(obra=self, completa =True)
        
        for p in planillas:
            if p.estado_incumplimiento():
                return p
        return None
    
    #devulve la ultima visita, si incumple devulve esa, si no incumple devulve la mas reciente del historial
    def ult_visita(self):
        try:
            return Planilla.objects.filter(obra=self.id, completa =True).earliest("fecha")
        except ObjectDoesNotExist:
            try:
                return HistorialPlanilla.objects.filter(obra=self.id).earliest("fecha")
            except ObjectDoesNotExist:
                return None
    
    def sin_visita(self):
        visita = self.ult_visita()
        if visita:
            return False
        else: return True
    
    def generar_nueva_planilla(self):
        if (self.sin_visita()):
            return True
        else:
            dif = date.today() - self.ult_visita().fecha
            if (dif.days >= 7):
                return True
        return False
    
    #Este va 
    def proximo_vencimiento_tipo(self, tipo):
        doc = self.documentos.filter(tipo=tipo).order_by('fecha_vencimiento').first()
        if doc:
            return doc.fecha_vencimiento
        return None

    #Este va 
    def estado_vencimiento_tipo(self, tipo): 
        doc = self.documentos.filter(tipo=tipo).order_by('fecha_vencimiento').first()
        return doc.estado_vencimiento()
    
    #Este va 
    def vencimiento_capacitacion(self):
        return self.proximo_vencimiento_tipo("CAPACITACION")

    #Este va 
    def vencimiento_simulacro(self):
        return self.proximo_vencimiento_tipo("SIMULACRO")

    #Este va 
    def vencimiento_epp(self):
        return self.proximo_vencimiento_tipo("EPP")

    #Este va 
    def vencimiento_aviso_de_obra(self):
        return self.proximo_vencimiento_tipo("AVISO_DE_OBRA")
    
    #Este va 
    def vencimiento_programa(self):
        return self.proximo_vencimiento_tipo("PROGRAMA")

    #Este va 
    def estado_capacitacion(self):
        return self.estado_vencimiento_tipo("CAPACITACION")

    #Este va 
    def estado_simulacro(self):
        return self.estado_vencimiento_tipo("SIMULACRO")

    #Este va 
    def estado_epp(self):
        return self.estado_vencimiento_tipo("EPP")

    #Este va 
    def estado_aviso_de_obra(self):
        return self.estado_vencimiento_tipo("AVISO_DE_OBRA")
    
    #Este va 
    def estado_programa(self):
        return self.estado_vencimiento_tipo("PROGRAMA")


    def documentos_a_vencer(self):
        tipos = ["CAPACITACION", "SIMULACRO", "EPP"]
        if self.sector not in ['AGRO', 'INDUSTRIA_COMERCIO']:
            tipos += ["AVISO_DE_OBRA", "PROGRAMA"]

        for tipo in tipos:
            doc = self.documentos.filter(tipo=tipo).order_by('fecha_vencimiento').first()
            if doc and doc.proximo_vencimiento():
                return True
        return False

    def documentos_cargados(self):
        tipos_requeridos = ["CAPACITACION", "SIMULACRO", "EPP"]

        if self.sector not in ['AGRO', 'INDUSTRIA_COMERCIO']:
            tipos_requeridos += ["AVISO_DE_OBRA", "PROGRAMA"]

        for tipo in tipos_requeridos:
            if not self.documentos.filter(tipo=tipo).first().fecha_vencimiento:
                return False
        return True

    

# Referido a documentos de habilitacion
class DocumentoObra(models.Model):  
    class Tipo(models.TextChoices):
        AVISO = "AVISO_DE_OBRA", "Aviso de obra - extensión"
        PROGRAMA = "PROGRAMA", "Programa de seguridad"
        PAT = "MEDICION_PAT", "Medición PAT"
        PULSO = "MEDICION_PULSO", "Medición pulso"
        RUIDOS = "MEDICION_RUIDOS", "Medición de ruidos"
        ILUMINACION = "MEDICION_ILUMINACION", "Medición de iluminación"
        ERGONOMIA = "ERGONOMIA", "Ergonomía"
        PLANO = "PLANO", "Plano de obra - extensión - demolición"
        MATAFUEGOS = "MATAFUEGOS", "Matafuegos"
        CAPACITACION = "CAPACITACION", "Capacitación"
        SIMULACRO = "SIMULACRO", "Simulacro"
        EPP = "EPP", "Epp"
        BALANCIN = "BALANCIN", "Balancin"
        SUELOS = "EST_DE SUELOS", "Est. de suelos"
        INFORME_TECNICO = "INFORME_TECNICO", "Informe técnico"
        AUTO_ELEVADOR = "AUTO_ELEVADOR", "Auto-elevador"
        MATERIAL_PARTICULADO = "MATERIAL_PARTICULADO", "Medición de material particulado"
        HOJAS_SEGURIDAD = "HOJAS_SEGURIDAD", "Hojas de seguridad"
        EVACUACION = "EVACUACION", "Plano de evacuación"
        HABITABILIDAD = "HABITABILIDAD", "Informe de habitabilidad"
        MAQUINARIAS = "MAQUINARIAS", "Maquinarias"
        RGRL = "RGRL", "RGRL"
        RAR = "RAR", "RAR"

    obra = models.ForeignKey(to=Obra, on_delete=models.CASCADE, related_name='documentos')
    fecha_carga = models.DateField(null=True, auto_now_add=True)
    fecha_vencimiento=models.DateField(null=True)
    tipo = models.CharField(max_length=30, choices=Tipo)
    doc = models.FileField(verbose_name='Documento', upload_to='documentos/', null=True)
    orden = models.IntegerField(auto_created=True)

    def __str__(self):
        return f"{self.tipo} de {self.obra} - Fecha {self.fecha_vencimiento}"
    
    #Este va
    def estado_vencimiento(self):
        if self.fecha_vencimiento:
            dif = self.fecha_vencimiento - date.today() 
            if (dif.days < 30):
                return "danger"
        
        return "dark"
    #Este va
    def proximo_vencimiento(self):
        if self.fecha_vencimiento:
            dif = self.fecha_vencimiento - date.today() 
            if (dif.days < 30):
                return True
        
        return False
    
    def save(self, *args, **kwargs):
        # Si hay un archivo anterior y se está actualizando el campo doc
        if self.pk:
            old_document = DocumentoObra.objects.get(pk=self.pk)
            if old_document.doc != self.doc:
                # Eliminar el archivo anterior
                if old_document.doc:
                    old_document.doc.delete(save=False)
        
        super(DocumentoObra, self).save(*args, **kwargs)
        
class Nomina(models.Model):
    CUIL = models.CharField(primary_key=True,validators= [RegexValidator(
                regex=r'[0-9]{11}$',
                message="Formato de CUIL incorrecto."
    )])
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    obra = models.ForeignKey(to=Obra, related_name='Nomina', on_delete=models.CASCADE)
    fecha_incorporacion = models.DateField(null=True)
        
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    


#Planilla que se completa a la hora de realizar una visita
class Planilla(models.Model):
    responsable_obra = models.CharField(null=True)
    obra = models.ForeignKey("Obra", on_delete=models.CASCADE, related_name='visitas')
    sector = models.CharField()
    fecha = models.DateField(null=True)
    comentarios = models.TextField( blank=True, default="")
    acciones = models.TextField(verbose_name="Acciones inmediatas", blank=True, null=True)
    verificacion = models.CharField( verbose_name="Verificación de las acciones tomadas", blank=True, null=True)
    fecha_efectiva = models.DateField(blank=True, null=True)
    completa = models.BooleanField(default=False)
    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f"Fecha: {self.fecha}"   
    
    def estado_incumplimiento(self):
        if self.completa:
            aspectos = AspectoSeguridad.objects.filter(planilla = self).exclude(ci=0)
            if aspectos and self.fecha_efectiva is None:
                return True
        return False
    
    def estado_urgencia(self):
        if self.completa:
            tipos_peligrosos = [
                'ANDAMIOS', 'ESCALERAS', 'ARNESES', 'LINEA_VIDA', 'POS_GOLPES',
                'ELECTRICIDAD', 'CABLES', 'EXCAVACIONES', 'BARABDAS', 'PLATAFORMAS_TRABAJO'
            ]

            aspectos = AspectoSeguridad.objects.filter(planilla=self, tipo__in=tipos_peligrosos)

            hay_ci_peligroso = any(
                aspecto.ci and aspecto.ci > 0
                for aspecto in aspectos
            )

            if hay_ci_peligroso:
                return "danger"

        return "secondary"


    def save(self, *args, **kwargs):
        es_edicion = self.pk is not None
        super().save(*args, **kwargs)  # Primero guardamos la planilla
        if es_edicion:
            # Verificamos si cumple con la condición para guardar el historial
            aspectos = self.aspectos.all()
            hay_ci = any(a.ci > 0 for a in aspectos)

            if not hay_ci or self.fecha_efectiva is not None and self.fecha: #no esta incompleta
                historiales = HistorialPlanilla.objects.filter(obra=self.obra).order_by('fecha')
                if historiales.count() >= 24:
                    historiales.first().delete()  # Borra el más antiguo
                # Generar el PDF
                archivo_pdf = generar_pdf_buffer(self)  # esto debería retornar un archivo en memoria

                # Guardar el PDF en Historial
                buffer = BytesIO(archivo_pdf) if isinstance(archivo_pdf, bytes) else archivo_pdf
                nombre_archivo = f"planilla_{self.obra}_{self.fecha}.pdf"

                HistorialPlanilla.objects.create(
                    obra=self.obra,
                    archivo = ContentFile(buffer.read(), nombre_archivo),
                    fecha = self.fecha
                )

                self.delete()

class AspectoSeguridad(models.Model):
    class TipoAspecto(models.TextChoices):
        ROPA_TRABAJO = "ropa_trabajo", "Uso de ropa de trabajo"
        EPP_BASICO = "epp_basico", "EPP básico"
        EPP_ACORDE = "epp_acorde", "EPP acorde a los trabajos"
        ESTADO_CONSERVACION = "estado_conservacion", "Estado y conservacion de los EPP"
        HERRAMIENTAS = "Herramientas", "Herramientas manuales"
        EQUIPOS = "Equipos", "Equipos manuales"
        EQUIPOS_MAQUINAS = "Equipos_maquinas", "Equipos y maquinas pesadas"
        ELECTRICIDAD = "Electricidad", "Tableros de electricidad"
        CABLES= "Cables", "Tendido de cables"
        EXCAVACIONES = "Excavaciones", "Excavaciones"
        BARANDAS = "Barandas", "Barandas perimetrales"
        PLATAFORMAS_TRABAJO = "Plataformas_trabajo", "Platafromas de trabajo"
        BOTIQUIN = "Botiquin", "Botiquin"
        COVID = "COVID", "Protocolo COVID-19"        
        ANDAMIOS = "andamios", "Andamios"
        ESCALERAS = "escaleras", "Escaleras"
        ARNESES = "arneses", "Uso y estado de arneses"
        LINEAS_VIDA = "Lineas_vida", "Líneas de vida"
        ORDEN_LIMPIEZA = "Oden_limpieza", "Órden y limpieza"
        PERMISO_TRABAJO = "Permiso_trabajo", "Permiso de trabajo"
        POS_GOLPES = "Pos_golpes", "Posib. de golpes, caídas, resbalones, etc"
        IZAJES_MANUALES = "Izajes_manuales", "Izajes manuales"
        IZAJES_EQUIPOS = "Izajes_equipos", "Izajes por equipos"
        DELIMITACION = "Delimitacion", "Delimitación de los trabajos"
        SENIALIZACION = "Señalizacion", "Señalización"
        EXTINTORES = "Extintores", "Extintores"
        LEGAJO_TECNICO = "Legajo_tecnico", "Legajo técnico"
        OTROS = "Otros", "Otros"

    planilla = models.ForeignKey(Planilla, on_delete=models.CASCADE, related_name="aspectos")
    tipo = models.CharField( choices=TipoAspecto.choices)
    cs = models.PositiveIntegerField(default=0)  # Cumple satisfactorio
    ci = models.PositiveIntegerField(default=0)  # Cumple insuficiente
    na = models.BooleanField(default=False)  # No aplica
    imagen = models.FileField(upload_to="planillas/", null=True, blank=True)
    
    def clean(self):
        """Si NA está activado, los valores de CS y CI deben ser 0."""
        if self.na and (self.cs > 0 or self.ci > 0):
            raise ValidationErr(f"Si 'No Aplica' está activado para {self.get_tipo_display()}, CS y CI deben ser 0.")

        if self.ci > 0 and not self.imagen:
            raise ValidationErr(f"Debés adjuntar una imagen si el aspecto '{self.get_tipo_display()}' tiene evaluación CI (cumple insuficiente).")
    def __str__(self):
        return f"{self.tipo}"

class HistorialPlanilla(models.Model):
    obra = models.ForeignKey("Obra", on_delete=models.CASCADE, related_name='historial_planillas')
    archivo = models.FileField(upload_to="historiales/")
    fecha = models.DateField()



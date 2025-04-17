from django.contrib import admin
from DASA.models import Planilla, ResponsableObra, Empresa, Obra, ART, AspectoSeguridad, DocumentoObra
# Register your models here.

class PlanillaUser(admin.ModelAdmin):
    exclude = ["hecha_por", "fecha"]
    # fields = [("obra", "sector"), ""]
    fieldsets = [
        (
            "Registro de observaciones",
            {
                "fields":["obra", "sector", "duracion"]
            }
        ),
        (
            "Opciones en caso de incumplimeintos",
            {
                "classes":["collapse"],
                "fields": ["comentarios", "acciones", "verificacion", "fecha_efectiva"]
            }
        )
    ]

admin.site.register(Planilla, PlanillaUser)
admin.site.register(Empresa)
admin.site.register(Obra)
admin.site.register(ResponsableObra)
admin.site.register(ART)
admin.site.register(AspectoSeguridad)

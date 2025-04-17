# Generated by Django 5.1.4 on 2025-03-03 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DASA', '0015_alter_obra_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aspectoseguridad',
            name='tipo',
            field=models.CharField(choices=[('ropa_trabajo', 'Uso de ropa de trabajo'), ('epp_basico', 'EPP básico'), ('epp_acorde', 'EPP acorde a los trabajos'), ('estado_conservacion', 'Estado y conservacion de los EPP'), ('Herramientas', 'Herramientas manuales'), ('Equipos', 'Equipos manuales'), ('Equipos_maquinas', 'Equipos y maquinas pesadas'), ('Electricidad', 'Tableros de electricidad'), ('Cables', 'Tendido de cables'), ('Excavaciones', 'Excavaciones'), ('Barandas', 'Barandas perimetrales'), ('Plataformas_trabajo', 'Platafromas de trabajo'), ('Botiquin', 'Botiquin'), ('COVID', 'Protocolo COVID-19'), ('andamios', 'Andamios'), ('escaleras', 'Escaleras'), ('arneses', 'Uso y estado de arneses'), ('Lineas_vida', 'Líneas de vida'), ('Oden_limpieza', 'Órden y limpieza'), ('Permiso_trabajo', 'Permiso de trabajo'), ('Pos_golpes', 'Posibilidad de golpes, caídas, resbalones, etc'), ('Izajes_manuales', 'Izajes manuales'), ('Izajes_equipos', 'Izajes por equipos'), ('Delimitacion', 'Delimitación de los trabajos'), ('Señalizacion', 'Señalización'), ('Extintores', 'Extintores'), ('Legajo_tecnico', 'Legajo técnico'), ('Otros', 'Otros')]),
        ),
    ]

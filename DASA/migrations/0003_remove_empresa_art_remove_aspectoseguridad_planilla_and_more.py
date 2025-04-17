# Generated by Django 5.1.4 on 2025-02-18 12:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DASA', '0002_rename_verfificacion_planilla_verificacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='empresa',
            name='art',
        ),
        migrations.RemoveField(
            model_name='aspectoseguridad',
            name='planilla',
        ),
        migrations.RemoveField(
            model_name='empresa',
            name='usuario',
        ),
        migrations.RemoveField(
            model_name='obra',
            name='empresa',
        ),
        migrations.RemoveField(
            model_name='historialdocumentoobra',
            name='obra',
        ),
        migrations.RemoveField(
            model_name='historialregulacionnomina',
            name='obra',
        ),
        migrations.RemoveField(
            model_name='presenteregulacion',
            name='regulacion',
        ),
        migrations.RemoveField(
            model_name='historialregulacionobra',
            name='obra',
        ),
        migrations.RemoveField(
            model_name='nomina',
            name='obra',
        ),
        migrations.RemoveField(
            model_name='presenteregulacion',
            name='CUIL',
        ),
        migrations.RemoveField(
            model_name='obra',
            name='firma',
        ),
        migrations.RemoveField(
            model_name='planilla',
            name='obra',
        ),
        migrations.RemoveField(
            model_name='planilla',
            name='hecha_por',
        ),
        migrations.RemoveField(
            model_name='responsableobra',
            name='usuario',
        ),
        migrations.DeleteModel(
            name='ART',
        ),
        migrations.DeleteModel(
            name='AspectoSeguridad',
        ),
        migrations.DeleteModel(
            name='Empresa',
        ),
        migrations.DeleteModel(
            name='HistorialDocumentoObra',
        ),
        migrations.DeleteModel(
            name='HistorialRegulacionNomina',
        ),
        migrations.DeleteModel(
            name='HistorialRegulacionObra',
        ),
        migrations.DeleteModel(
            name='Nomina',
        ),
        migrations.DeleteModel(
            name='PresenteRegulacion',
        ),
        migrations.DeleteModel(
            name='Obra',
        ),
        migrations.DeleteModel(
            name='Planilla',
        ),
        migrations.DeleteModel(
            name='ResponsableObra',
        ),
    ]

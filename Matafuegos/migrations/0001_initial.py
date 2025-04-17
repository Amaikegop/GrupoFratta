# Generated by Django 5.1.4 on 2025-01-14 20:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Matafuego',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=50, unique=True, verbose_name='Código del Matafuego')),
                ('tipo', models.CharField(max_length=100, verbose_name='Tipo de Matafuego')),
                ('capacidad', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Capacidad (kg)')),
                ('fecha_compra', models.DateField(verbose_name='Fecha de Compra')),
                ('fecha_ultima_recarga', models.DateField(verbose_name='Fecha Última Recarga')),
                ('fecha_vencimiento', models.DateField(verbose_name='Fecha de Vencimiento')),
                ('ubicacion', models.CharField(max_length=255, verbose_name='Ubicación')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones Adicionales')),
                ('responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Responsable de Supervisión')),
            ],
            options={
                'verbose_name': 'Matafuego',
                'verbose_name_plural': 'Matafuegos',
                'ordering': ['fecha_vencimiento'],
            },
        ),
        migrations.CreateModel(
            name='AlertaVencimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_alerta', models.DateField(verbose_name='Fecha de Alerta Generada')),
                ('enviada', models.BooleanField(default=False, verbose_name='¿Alerta Enviada?')),
                ('matafuego', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='alerta', to='Matafuegos.matafuego')),
            ],
            options={
                'verbose_name': 'Alerta de Vencimiento',
                'verbose_name_plural': 'Alertas de Vencimiento',
            },
        ),
        migrations.CreateModel(
            name='RegistroMantenimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True, verbose_name='Fecha del Mantenimiento')),
                ('descripcion', models.TextField(verbose_name='Descripción del Mantenimiento')),
                ('realizado_por', models.CharField(max_length=100, verbose_name='Realizado Por')),
                ('costo', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Costo del Mantenimiento')),
                ('matafuego', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mantenimientos', to='Matafuegos.matafuego')),
            ],
            options={
                'verbose_name': 'Registro de Mantenimiento',
                'verbose_name_plural': 'Registros de Mantenimiento',
                'ordering': ['-fecha'],
            },
        ),
    ]

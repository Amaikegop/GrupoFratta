# Generated by Django 5.1.4 on 2025-04-15 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DASA', '0035_remove_responsableobra_id_alter_responsableobra_cuil'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='planilla',
            name='duracion',
        ),
    ]

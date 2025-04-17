# Generated by Django 5.1.4 on 2025-04-14 15:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DASA', '0032_alter_nomina_fecha_incorporacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nomina',
            name='id',
        ),
        migrations.AlterField(
            model_name='nomina',
            name='CUIL',
            field=models.CharField(primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='Formato de CUIL incorrecto.', regex='[0-9]{11}$')]),
        ),
    ]

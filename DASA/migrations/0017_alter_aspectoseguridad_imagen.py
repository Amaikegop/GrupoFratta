# Generated by Django 5.1.4 on 2025-03-04 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DASA', '0016_alter_aspectoseguridad_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aspectoseguridad',
            name='imagen',
            field=models.FileField(blank=True, null=True, upload_to='planillas/'),
        ),
    ]

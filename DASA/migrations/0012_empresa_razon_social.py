# Generated by Django 5.1.4 on 2025-03-01 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DASA', '0011_remove_empresa_razon_social_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='razon_social',
            field=models.CharField(default='', max_length=150),
        ),
    ]

# Generated by Django 5.0.4 on 2024-05-07 15:54

import websitebuilder.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websitebuilder', '0017_cliente_code_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='code_client',
            field=models.CharField(default=websitebuilder.models.generate_cliente_code, max_length=100, null=True),
        ),
    ]
# Generated by Django 5.0.4 on 2024-05-08 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websitebuilder', '0033_achatsupport_updated_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandesupport',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='websitebuilder.administrateur'),
        ),
    ]
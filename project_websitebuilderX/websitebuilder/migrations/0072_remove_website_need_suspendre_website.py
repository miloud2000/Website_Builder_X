# Generated by Django 5.0.4 on 2024-06-05 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('websitebuilder', '0071_alter_locationwebsitebuilder_statu_du_website_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='website_need_suspendre',
            name='website',
        ),
    ]
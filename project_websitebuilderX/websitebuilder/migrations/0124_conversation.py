# Generated by Django 5.0.7 on 2024-07-25 12:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websitebuilder', '0123_delete_conversation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_type', models.CharField(choices=[('Cliente', 'Cliente'), ('SupportTechnique', 'SupportTechnique')], max_length=20)),
                ('sender_id', models.PositiveIntegerField()),
                ('message', models.TextField(max_length=2000)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to='websitebuilder.ticket')),
            ],
        ),
    ]

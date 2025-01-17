# Generated by Django 5.0.7 on 2024-07-25 12:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websitebuilder', '0121_rename_supportname_ticket_supportname'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(max_length=2000)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('sender_support', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='websitebuilder.supporttechnique')),
                ('sender_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to='websitebuilder.ticket')),
            ],
        ),
    ]

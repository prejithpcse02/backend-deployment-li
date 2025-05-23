# Generated by Django 5.1.7 on 2025-04-24 04:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
        ('offers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_offer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='offer_messages', to='offers.offer'),
        ),
    ]

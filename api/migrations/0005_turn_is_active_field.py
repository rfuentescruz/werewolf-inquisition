# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-20 15:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_player_is_owner_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='active_turn',
        ),
        migrations.AddField(
            model_name='turn',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]

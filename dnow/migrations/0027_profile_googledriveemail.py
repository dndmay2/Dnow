# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-09 03:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0026_auto_20181108_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='googleDriveEmail',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]

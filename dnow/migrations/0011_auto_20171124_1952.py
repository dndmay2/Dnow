# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-25 01:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0010_auto_20171124_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cook',
            name='mealHostHomes',
            field=models.ManyToManyField(blank=True, to='dnow.HostHome'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-01-12 01:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0023_auto_20180103_2128'),
    ]

    operations = [
        migrations.AddField(
            model_name='hosthome',
            name='color',
            field=models.CharField(default='', max_length=20),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-12 15:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0039_auto_20190109_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='subject',
            field=models.CharField(default='', max_length=200),
        ),
    ]

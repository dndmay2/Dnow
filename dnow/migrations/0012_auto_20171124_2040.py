# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-25 02:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0011_auto_20171124_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='hosthome',
            name='cook1LastName',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='hosthome',
            name='cook2LastName',
            field=models.CharField(default='', max_length=30),
        ),
    ]

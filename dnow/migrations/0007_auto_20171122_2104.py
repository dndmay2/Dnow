# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-23 03:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0006_auto_20171122_2051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hosthome',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=16),
        ),
    ]

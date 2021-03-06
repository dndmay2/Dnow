# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-17 04:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0031_auto_20181117_0013'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('greeting', models.TextField(blank=True)),
                ('closing', models.TextField(blank=True)),
                ('toGroups', models.CharField(choices=[('hostHomes', 'Host Homes'), ('parents', 'Parents'), ('drivers', 'Drivers'), ('leaders', 'Leaders'), ('students', 'Students')], default='?', max_length=50)),
                ('includeData', models.CharField(choices=[('hostHomeBasics', 'Host Home Basics'), ('churchStaff', 'Church Staff'), ('cooks', 'Cooks'), ('driverData', 'Driver Data'), ('leaders', 'Leaders'), ('students', 'Students'), ('tshirts', 'T-Shirts')], default='?', max_length=30)),
            ],
        ),
    ]

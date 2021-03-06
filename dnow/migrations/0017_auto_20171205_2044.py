# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-06 02:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0016_driveslot_meal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driveslot',
            name='driver',
        ),
        migrations.AddField(
            model_name='driveslot',
            name='drivers',
            field=models.ManyToManyField(to='dnow.Driver'),
        ),
        migrations.AlterField(
            model_name='cook',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=4),
        ),
        migrations.AlterField(
            model_name='driver',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=4),
        ),
        migrations.AlterField(
            model_name='hosthome',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=16),
        ),
        migrations.AlterField(
            model_name='leader',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=16),
        ),
        migrations.AlterField(
            model_name='student',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=16),
        ),
    ]

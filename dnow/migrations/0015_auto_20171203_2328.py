# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-04 05:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnow', '0014_remove_driver_hosthome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cook',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('X Large', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=4),
        ),
        migrations.AlterField(
            model_name='driver',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('X Large', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=4),
        ),
        migrations.AlterField(
            model_name='hosthome',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('X Large', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=16),
        ),
        migrations.AlterField(
            model_name='leader',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('X Large', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=16),
        ),
        migrations.AlterField(
            model_name='student',
            name='tshirtSize',
            field=models.CharField(choices=[('Small', 'S'), ('Med', 'M'), ('Large', 'L'), ('XL', 'XL'), ('X Large', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], default='M', max_length=16),
        ),
    ]

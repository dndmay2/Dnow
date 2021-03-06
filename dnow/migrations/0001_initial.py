# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-21 03:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import localflavor.us.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HostHome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(default='', max_length=30)),
                ('lastName', models.CharField(default='', max_length=30)),
                ('phone', localflavor.us.models.PhoneNumberField(default='', max_length=20)),
                ('email', models.EmailField(default='', max_length=254)),
                ('street', models.CharField(default='', max_length=255)),
                ('city', models.CharField(default='Fairview', max_length=90)),
                ('state', localflavor.us.models.USStateField(default='TX', max_length=2)),
                ('zipCode', localflavor.us.models.USZipCodeField(default='75069', max_length=10)),
                ('grade', models.CharField(choices=[('?', '?'), ('7', '7th'), ('8', '8th'), ('9', '9th'), ('10', '10th'), ('11', '11th'), ('12', '12th')], default='?', max_length=15)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=2)),
                ('bgCheck', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(default='', max_length=30)),
                ('lastName', models.CharField(default='', max_length=30)),
                ('phone', localflavor.us.models.PhoneNumberField(default='', max_length=20)),
                ('email', models.EmailField(default='', max_length=254)),
                ('street', models.CharField(default='', max_length=255)),
                ('city', models.CharField(default='Fairview', max_length=90)),
                ('state', localflavor.us.models.USStateField(default='TX', max_length=2)),
                ('zipCode', localflavor.us.models.USZipCodeField(default='75069', max_length=10)),
                ('host', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(default='', max_length=30)),
                ('lastName', models.CharField(default='', max_length=30)),
                ('phone', localflavor.us.models.PhoneNumberField(default='', max_length=20)),
                ('email', models.EmailField(default='', max_length=254)),
                ('street', models.CharField(default='', max_length=255)),
                ('city', models.CharField(default='Fairview', max_length=90)),
                ('state', localflavor.us.models.USStateField(default='TX', max_length=2)),
                ('zipCode', localflavor.us.models.USZipCodeField(default='75069', max_length=10)),
                ('friendName', models.CharField(default='', max_length=40)),
                ('grade', models.CharField(choices=[('?', '?'), ('7', '7th'), ('8', '8th'), ('9', '9th'), ('10', '10th'), ('11', '11th'), ('12', '12th')], default='?', max_length=2)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=2)),
                ('dateRegistered', models.DateField(blank=True, null=True)),
                ('amountPaid', models.DecimalField(decimal_places=2, default=0.0, max_digits=4)),
                ('churchMember', models.BooleanField(default=False)),
                ('medicalForm', models.BooleanField(default=False)),
                ('tshirtSize', models.BooleanField(default=False)),
                ('hostHome', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dnow.HostHome')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dnow.Parent')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='hosthome',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dnow.Parent'),
        ),
    ]

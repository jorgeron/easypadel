# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-31 14:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easypadel', '0060_auto_20170531_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jugador',
            name='partidos_ganados',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=4),
        ),
        migrations.AlterField(
            model_name='jugador',
            name='partidos_jugados',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=4, null=True),
        ),
    ]
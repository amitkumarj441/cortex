# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-12 13:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cortex', '0011_auto_20160925_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='source',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='articles', related_query_name='article', to='cortex.AllUrl'),
            preserve_default=False,
        ),
    ]

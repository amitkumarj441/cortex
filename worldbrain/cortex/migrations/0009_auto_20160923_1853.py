# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-23 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cortex', '0008_auto_20160923_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='last_time_crawled',
            field=models.DateTimeField(null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-17 10:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cortex', '0005_source_processed_spider'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='ready_for_crawling',
            field=models.BooleanField(default=False),
        ),
    ]
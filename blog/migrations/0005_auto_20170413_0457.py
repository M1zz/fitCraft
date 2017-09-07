# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_profile_last_sync_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='fitHeart',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='fitSleep',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_sync_date',
            field=models.DateTimeField(default=b'2017-03-09 00:00:00', blank=True),
        ),
    ]

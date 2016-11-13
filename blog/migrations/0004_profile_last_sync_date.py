# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_sync_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]

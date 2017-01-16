# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-04 16:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0004_auto_20170104_1502'),
    ]

    operations = [
        migrations.CreateModel(
            name='StartupPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Startup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_mode', models.IntegerField(choices=[(0, 'Blacklist'), (1, 'Whitelist')], default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='startuppermission',
            unique_together=set([('user', 'startup')]),
        ),
    ]

# Generated by Django 5.1.1 on 2024-09-14 18:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiRequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username_persistent', models.CharField(blank=True, max_length=200, null=True)),
                ('requested_at', models.DateTimeField(db_index=True)),
                ('response_ms', models.PositiveIntegerField(default=0)),
                ('path', models.CharField(db_index=True, help_text='api url path', max_length=200)),
                ('view', models.CharField(blank=True, db_index=True, help_text='view called by this endpoint', max_length=200, null=True)),
                ('view_method', models.CharField(blank=True, db_index=True, max_length=200, null=True)),
                ('remote_addr', models.GenericIPAddressField()),
                ('host', models.URLField()),
                ('method', models.CharField(max_length=10)),
                ('query_params', models.TextField(blank=True, null=True)),
                ('data', models.TextField(blank=True, null=True)),
                ('response', models.TextField(blank=True, null=True)),
                ('errors', models.TextField(blank=True, null=True)),
                ('status_code', models.PositiveIntegerField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

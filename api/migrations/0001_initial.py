# Generated by Django 3.2.23 on 2024-12-12 19:47

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FuelStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('address', models.CharField(default='', max_length=255)),
                ('city', models.CharField(default='', max_length=100)),
                ('state', models.CharField(default='', max_length=2)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('rack_id', models.CharField(default='', max_length=255)),
                ('retail_price', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]

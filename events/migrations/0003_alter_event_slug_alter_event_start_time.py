# Generated by Django 5.0.6 on 2024-07-04 16:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_alter_event_start_time_ticket_unique_event_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 5, 16, 57, 42, 764949, tzinfo=datetime.timezone.utc)),
        ),
    ]

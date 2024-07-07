# Generated by Django 5.0.6 on 2024-07-05 17:02

import events.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_event_slug_alter_event_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='no_of_participants',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(default=events.models.Event.get_default_time),
        ),
    ]
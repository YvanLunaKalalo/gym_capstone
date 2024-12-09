# Generated by Django 4.2.15 on 2024-12-10 17:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0015_alter_userprogress_options_userprogress_time_spent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprogress',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprogress',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='userprogress',
            name='time_spent',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

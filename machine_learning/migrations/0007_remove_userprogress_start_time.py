# Generated by Django 4.2.15 on 2024-12-02 18:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0006_userprogress_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprogress',
            name='start_time',
        ),
    ]

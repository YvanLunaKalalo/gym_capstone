# Generated by Django 4.2.15 on 2024-11-30 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0002_userprogress_is_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprogress',
            name='is_completed',
        ),
    ]
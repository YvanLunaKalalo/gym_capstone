# Generated by Django 4.2.15 on 2024-11-30 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprogress',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
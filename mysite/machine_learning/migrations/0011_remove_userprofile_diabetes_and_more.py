# Generated by Django 4.2.15 on 2024-10-14 07:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0010_userprogress_progress_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='Diabetes',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='Fitness_Goal',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='Fitness_Type',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='Hypertension',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='Level',
        ),
    ]

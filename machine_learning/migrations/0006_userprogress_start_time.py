# Generated by Django 4.2.15 on 2024-12-02 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0005_remove_userprogress_completed_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprogress',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

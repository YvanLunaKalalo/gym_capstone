# Generated by Django 4.2.15 on 2024-11-20 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0019_alter_userprofile_sex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='Fitness_Type',
            field=models.CharField(default='Cardio_Fitness', max_length=50),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='Level',
            field=models.CharField(default='Normal', max_length=50),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='Sex',
            field=models.CharField(max_length=10),
        ),
    ]

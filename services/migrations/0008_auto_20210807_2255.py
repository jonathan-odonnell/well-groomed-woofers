# Generated by Django 3.2.5 on 2021-08-07 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_auto_20210806_2255'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='availability',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='availability',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='availability',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='availability',
            name='start_time',
        ),
        migrations.AddField(
            model_name='availability',
            name='end_time',
            field=models.DateTimeField(),
        ),
        migrations.AddField(
            model_name='availability',
            name='start_time',
            field=models.DateTimeField(),
        ),
    ]

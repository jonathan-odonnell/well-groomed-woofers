# Generated by Django 3.2.5 on 2021-08-15 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_pet_user_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pet',
            name='breed',
        ),
        migrations.RemoveField(
            model_name='pet',
            name='user_profile',
        ),
        migrations.DeleteModel(
            name='Breed',
        ),
        migrations.DeleteModel(
            name='Pet',
        ),
    ]

# Generated by Django 3.2.5 on 2021-08-15 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_breed_pet'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='user_profile',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='profiles.userprofile'),
            preserve_default=False,
        ),
    ]
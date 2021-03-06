# Generated by Django 3.1.3 on 2021-07-26 21:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=20, region=None)),
                ('address_line_1', models.CharField(max_length=80)),
                ('address_line_2', models.CharField(blank=True, max_length=80, null=True)),
                ('town_or_city', models.CharField(max_length=40)),
                ('county', models.CharField(max_length=80)),
                ('postcode', models.CharField(max_length=20)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

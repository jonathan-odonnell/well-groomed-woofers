# Generated by Django 3.2.5 on 2021-08-15 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0011_auto_20210815_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlineitem',
            name='size',
            field=models.CharField(max_length=20),
        ),
    ]

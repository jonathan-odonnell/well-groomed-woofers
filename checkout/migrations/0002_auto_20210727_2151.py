# Generated by Django 3.1.3 on 2021-07-27 20:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='street_address1',
            new_name='address_line_1',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='street_address2',
            new_name='address_line_2',
        ),
    ]

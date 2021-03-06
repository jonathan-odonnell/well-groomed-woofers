# Generated by Django 3.1.3 on 2021-08-10 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0010_orderlineitem_price'),
        ('services', '0009_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to='checkout.order'),
        ),
    ]

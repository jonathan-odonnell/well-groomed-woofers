# Generated by Django 3.2.5 on 2021-09-05 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210820_1610'),
        ('services', '0018_auto_20210820_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='order_lineitem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='orders.orderlineitem'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='taxi',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='orders.order'),
        ),
    ]
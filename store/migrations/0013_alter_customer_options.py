# Generated by Django 5.0.4 on 2024-04-18 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_alter_order_options_alter_customer_membership'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['user__first_name', 'user__last_name'], 'permissions': [('view_history', 'Can view history')]},
        ),
    ]

# Generated by Django 3.2.16 on 2023-03-19 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('djstripe', '0010_alter_customer_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingCustomer',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.customer', to_field='id')),
                ('subscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.subscription', to_field='id')),
            ],
        ),
    ]

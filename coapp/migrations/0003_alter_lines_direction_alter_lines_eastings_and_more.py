# Generated by Django 4.2.7 on 2023-11-26 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coapp', '0002_alter_parcel_name_of_allottee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lines',
            name='Direction',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lines',
            name='Eastings',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lines',
            name='FromBeaconNo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lines',
            name='InternalAngle',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='lines',
            name='Length',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lines',
            name='Northings',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lines',
            name='OBJECTID',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lines',
            name='Sequence',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='lines',
            name='ToBeaconNo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
# Generated by Django 4.2.7 on 2023-11-29 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lines',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
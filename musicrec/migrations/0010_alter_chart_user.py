# Generated by Django 4.2.7 on 2025-03-22 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicrec', '0009_chart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='user',
            field=models.CharField(max_length=50),
        ),
    ]

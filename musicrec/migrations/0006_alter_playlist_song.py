# Generated by Django 4.2.7 on 2025-03-18 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musicrec', '0005_alter_playlist_collaborative'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='song',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='musicrec.song'),
        ),
    ]

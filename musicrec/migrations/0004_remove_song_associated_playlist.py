# Generated by Django 4.2.7 on 2025-03-18 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicrec', '0003_song_alter_playlist_song'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='associated_playlist',
        ),
    ]

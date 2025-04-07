from django.db import models

class Playlist(models.Model):
    user = models.CharField(max_length=50)
    time_created = models.DateTimeField(auto_now_add=True)
    playlist_name = models.CharField(max_length=50)
    playlist_public = models.CharField(max_length=7)
    collaborative = models.CharField(max_length=3)
    playlist_id = models.CharField(max_length=50, blank=True)

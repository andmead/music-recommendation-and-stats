from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('callback/', views.callback, name='callback'),
    path('recommend/', views.artist_rec, name='recommend'),
    path('playlist/', views.user_playlists_view, name='userplaylists'),
    path('playlist/<str:id>', views.playlist_view, name='playlistview'),
    path('playlist/create/', views.create_playlist, name='createplaylist'),
    path('callback/', views.callback, name='callback'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('userstats/', views.user_stats, name='userstats'),
    path('search/', views.artist_search, name='artistsearch'),
    path('top/<str:id>', views.artist_top_songs, name='artisttop'),
]
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import spotipy
import pandas as pd
from spotipy import cache_handler
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import DjangoSessionCacheHandler
from .models import *
from finalproject.settings import client_id, client_secret, BASE_URL


def index(request):
    return render(request, 'musicrec/index.html')


def login_view(request):
    next_url = request.GET.get('next', 'index')
    request.session['next_url'] = next_url
    
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
        show_dialog=True
    )
    
    token = sp_oauth.validate_token(sp_oauth.cache_handler.get_cached_token())
    if token:
        return redirect(next_url)
    else:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
   
def callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
        show_dialog=True
    )
    
    code = request.GET.get('code')
    if code:
        token = sp_oauth.get_access_token(code)
        next_url = request.session.get('next_url', 'index')
        
        if 'next_url' in request.session:
            del request.session['next_url']
            
        return redirect(next_url)
    
    #if auth fails
    return redirect('index')


def artist_rec(request):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
    )
    
    spotify = Spotify(auth_manager=sp_oauth)
    top_artists_query = spotify.current_user_top_artists(limit=50, offset=0, time_range='short_term')
    
    artist_genres = []
    for i in top_artists_query['items']:
        for g in i['genres']:
            artist_genres.append(g)

    df = pd.DataFrame(artist_genres, columns=['genre'])
    percentage = df['genre'].value_counts(normalize=True) * 100
    rounded = round(percentage, 2)
    count = rounded.head(3)
    count_list = count.index.tolist()
    recommendations = []
    
    for i in count_list:
        search = spotify.search(q=f'genre:{i}', type='track', limit=20)
        recommendations.extend(search['tracks']['items'])
    
    return render(request, 'musicrec/artistrec.html', {
        'count': count, 'count_list': count_list, 'recommendations': recommendations, 'search': search
    })


def create_playlist(request):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
    )
    
    spotify = Spotify(auth_manager=sp_oauth)
    user_id = spotify.current_user()['id']
    
    top_songs_query = spotify.current_user_top_tracks(limit=50, offset=0, time_range='short_term')
    top_artists_query = spotify.current_user_top_artists(limit=50, offset=0, time_range='short_term')
    
    artist_genres = []
    for i in top_artists_query['items']:
        for g in i['genres']:
            artist_genres.append(g)

    df = pd.DataFrame(artist_genres, columns=['genre'])
    percentage = df['genre'].value_counts(normalize=True) * 100
    rounded = round(percentage, 2)
    count = rounded.head(3)
    count_list = count.index.tolist()
    recommendations = []     
    
    
    if request.method == "POST":
        playlist_name = request.POST.get('playlist-name')
        public_private = request.POST.get('public-private')
        collaborative = request.POST.get('collab')
        description = request.POST.get('description')
        new_playlist = spotify.user_playlist_create(user=user_id, name=playlist_name, public=public_private, collaborative=collaborative, description=description)
        playlist_id = new_playlist['id']
        
        
        for i in count_list:
            search = spotify.search(q=f'genre:{i}', type='track', limit=50)
            tracks = search['tracks']['items']
        
       
        for item in tracks:
            if spotify.current_user_saved_tracks_contains(tracks=[item['id']])[0]:
                continue
            else:
                recommendations.append(item)
        
        
        if len(recommendations) < 50:
            song_genres = []
            artist_from_songs = []
            for i in top_songs_query['items']:
                for a in i['artists']:
                    artist_from_songs.extend(spotify.artist(a['id']))
                    
            for g in artist_from_songs:
                song_genres.append(g)

            df_song = pd.DataFrame(song_genres, columns=['genre'])
            percentage = df_song['genre'].value_counts(normalize=True) * 100
            rounded_song = round(percentage, 2)
            count_song = rounded_song.head(3)
            count_list_song = count_song.index.tolist()
            
            for i in count_list_song:
                search_song = spotify.search(q=f'genre:{i}', type='track', limit=50)
                tracks_song_list = search_song['tracks']['items']
            
            for item in tracks_song_list:
                if spotify.current_user_saved_tracks_contains(tracks=[item['id']])[0]:
                    continue
                else:
                    recommendations.append(item)

        for song in recommendations:
            song_id = song['id']
            add_songs = spotify.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=[song_id])
        
        new_playlist_object = Playlist.objects.create(user=user_id, playlist_name=playlist_name, playlist_public=public_private, collaborative=collaborative, playlist_id=playlist_id)
        return redirect('userplaylists')
        
    return render(request, 'musicrec/createplaylist.html', {
        "recommendations": recommendations
    })


def user_playlists_view(request):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
    )
    
    spotify = Spotify(auth_manager=sp_oauth)
    playlists = spotify.current_user_playlists()
    pl_list = []
    user_id = spotify.current_user()['id']
    
    while playlists:
        for playlist in playlists['items']:
            if playlist['owner']['id'] == user_id:
                pl_list.append(playlist)
                
                
        if playlists['next']:
            playlists = spotify.next(playlists)
        else:
            playlists = None
    
    return render(request, 'musicrec/userplaylists.html', {
        'pl_list': pl_list, 'playlists': playlists
    })


def playlist_view(request, id):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
    )
    
    spotify = Spotify(auth_manager=sp_oauth)
    user_id = spotify.current_user()['id']
    
    playlist = spotify.playlist_tracks(playlist_id=id, fields="items.track.name, items.track.artists.name")
    playlist_tracks = playlist['items']
    playlist_info = spotify.playlist(playlist_id=id, fields="name")
    playlist_name = playlist_info['name']
    
    return render(request, 'musicrec/playlist.html', {
        'playlist_tracks': playlist_tracks, "playlist_name": playlist_name
    })


def artist_top_songs(request, id):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
    )
    
    spotify = Spotify(auth_manager=sp_oauth)
    
    artist = spotify.artist_top_tracks(artist_id=id)
    artist_name = spotify.artist(artist_id=id)
    artist_tracks = []
    
    for track in artist['tracks']:
        artist_tracks.append(track['name'])

    
    return render(request, 'musicrec/artisttop.html', {
        "artist_tracks": artist_tracks, "artist_name": artist_name
    })


def artist_search(request):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
    )
    spotify = Spotify(auth_manager=sp_oauth)
    search_query = None
    unique_artists = []
    
    if request.method == "POST":
        search_bar = request.POST.get('search_bar')
        search_query = spotify.search(q=search_bar, type="artist", limit=20)
        
        if search_query and "artists" in search_query and "items" in search_query["artists"]:
            seen_names = set()
            for artist in search_query["artists"]["items"]:
                if artist["name"].lower() not in seen_names:
                    seen_names.add(artist["name"].lower())
                    unique_artists.append(artist)  
        
        return render(request, 'musicrec/search.html', {
            'search_query': search_query, 'unique_artists': unique_artists
        })
    
    return render(request, 'musicrec/topsongs.html')


def statistics_view(request):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
    )
    
    spotify = Spotify(auth_manager=sp_oauth)
    user_name = spotify.current_user()['display_name']
    
    top_songs_query = spotify.current_user_top_tracks(limit=50, offset=0, time_range='short_term')
    songs = top_songs_query['items']
    top_artists_query = spotify.current_user_top_artists(limit=50, offset=0, time_range='short_term')
    artists = top_artists_query['items']
    
    return render(request, 'musicrec/usertopsongs.html', {
        'user_name': user_name, 'songs': songs, 'artists': artists,
    })


def user_stats(request):
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{BASE_URL}/callback",
        scope='playlist-modify-public playlist-read-private playlist-modify-private user-library-read user-library-modify user-read-recently-played user-top-read user-read-email',
        cache_handler=DjangoSessionCacheHandler(request),
    )
    
    spotify = Spotify(auth_manager=sp_oauth)
    top_songs_query = spotify.current_user_top_tracks(limit=50, offset=0, time_range='short_term')
    top_artists_query = spotify.current_user_top_artists(limit=50, offset=0, time_range='short_term')
    songs = top_songs_query['items']
    artists = top_artists_query['items']
    
    
    songs_by_artists = []
    for i in top_songs_query['items']:
        for s in i['artists']:
            songs_by_artists.append(s)
    
    artist_genres = []
    for i in top_artists_query['items']:
        for g in i['genres']:
            artist_genres.append(g)

    df = pd.DataFrame(artist_genres, columns=['genre'])    
    percentage = df['genre'].value_counts(normalize=True) * 100
    rounded = round(percentage, 2)
    count = rounded.head(5)
    genre_labels = count.index.tolist()
    genre_values = count.values.tolist()
    
    df_songs = pd.DataFrame(songs_by_artists, columns=['name'])
    df_songs_counts = df_songs['name'].value_counts()
    df_songs_count = df_songs_counts.head(5)
    song_labels = df_songs_count.index.tolist()
    song_values = df_songs_count.values.tolist()
    
    return JsonResponse({
        'genre_labels': genre_labels, 'genre_values': genre_values, 'songs_by_artists': songs_by_artists, 'song_labels': song_labels,
        'song_values': song_values, 'artists': artists, 'songs': songs   
    })
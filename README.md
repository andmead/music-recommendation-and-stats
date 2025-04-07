# Streamboat (CS50 Web Development Capstone Project)

## Distinctiveness and Complexity

I feel that my project "Streamboat" satisfies the "Distinctiveness and Complexity" requirements for a few reasons:

1. I made use of a 3rd party API (Spotify's web API).
2. Using said API, I made use of their OAuth2 implementation to allow the user to accept my app to access aspects of their account's data.
3. Also pertaining to the API, I made use of environment variables with a .env file to store the Client_Secret and Client_ID needed for OAuth.
4. Outside of the API it's self, I made an effort to learn and use a few new libraries (Chart.JS, Pandas, and especially Spotipy).
5. And finally, to ensure that everything needed to run the program on other systems was in place, I set up a Docker container to test my app.

As for what specifically makes me believe this is sufficiently distinct when compared to the other programs we have created in the CS50 Web Development course, I feel that the use of a real world API that can make tangible changes to an account (creating a playlist on my Spotify account for example), as well as displaying data within graphs builds off what we learned in the rest of the course. I used aspects that I learned from all of the other projects to create something that, to me, feels like a culmination of a lot of smaller parts, with a new way of displaying certain information to the user.


# How To Run

1. Git clone the repository
2. Set up the virtual environment <br>
`python -m venv venv`<br>
`venv\Scripts\activate` (if on Windows)<br> 
`source venv/bin/activate` (if on Mac or Linux)
3. Install dependencies `pip install -r requirements.txt`
4. Apply migrations `python manage.py migrate`
5. Run server `python manage.py runserver`
6. When you click on any of the buttons if you have not authorized use of your Spotify account you will be taken to the official Spotify authentication page to accept or decline access to certain data. <br>

After that you can use all aspects of the app!

# Finalproject Directory


## Settings.py

Within the settings.py file I added a few things. Firstly the obvious, adding 'musicrec' (my project dir name) to the installed apps list. Then I imported load_dotenv from dotenv and made a call to the load_dotenv function, so I could assign my client_id and client_secret to variables to be used within the rest of my app. I also assigned a BASE_URL and some CSRF_TRUSTED_ORIGINS as I was having issues with Docker and this seemed to fix it. 

# Musicrec Directory

## Models.py

There is only one Model and that is the "Playlist" model. This just saves the user who created the playlist, time it was created, the playlist name, whether it is public or private, collaborative or not, and the playlist_id.

## Views.py

### index

The index view just displays the index.html file to the user so they can navigate the application.

### login_view

The login_view checks for a valid access token, if it finds one, the user is redirected to the page they were trying to access, if there is not a valid token they are redirected to the authorization page.

### callback

The callback view is used for the OAuth2 process to redirect back to the app (Streamboat) after user authentication via Spotify has been either completed, failed, or canceled.

### artist_rec

The artist_rec view gets the user's Spotify account and queries for their top artists, loops through the top artists and appends the genres to a list which is then turned into a Pandas dataframe. Using that Pandas dataframe, we find the percentage that genre appears in the user's top 50 artists (eg: hip-hop 20%/100%), and then take the top three genres and convert the Pandas series to a list. 

With that new genre list, we create another list for the recommendations, loop through the genre list searching for tracks with the same genre, and extend the recommendations list with the results. I'm sure there's a better way of doing this, but Spotify's official recommendation API path has been deprecated, and this was what I came up with. I'm decently happy with the results I get with it, though I may revisit this in the future.

### create_playlist

Within the create_playlist view we use similar logic as the artist_rec view to GET recommendations for the user. Then when a user makes a POST request to create a playlist through the createplaylist.html template we get the information the user entered into the form (the playlist name, public/private, collaborative or not, and description) and using the Spotipy library we create a new playlist plugging in those values for the corresponding argument.

Once created, we get the id of the new playlist and using the logic from artist_rec, we search for tracks by genre in the user's top three, and then loop through those tracks and check if the user has those tracks "saved". If the tracks are "saved" by the user, we skip the track and continue to find something that hopefully the user may have not heard before. Tracks that are not saved by the user are appended to a recommendations list.

If the recommendations list length is less than 50,  the function will query for the user's top 50 songs, extract the artists from the songs and extend them to a list, and loop through that list using the same logic we used earlier to get the top three genres from the top artists query, to get more songs to recommend.

Once the recommendations list is at or above 50 tracks, we then use a for loop to get the id of each song, and add the the song to the playlist. Once all songs are added we create a new playlist object for our Playlist model which saves the user id, playlist name, public/private status, collaborative status, and the playlist id.

### user_playlists_view

The user_playlists_view gets all the playlists created by the user, appends them to a list and then the list is added to the context to display the list of playlist names on the userplaylists.html template. 

### playlist_view

When a playlist is clicked on from the userplaylists.html template, the user is taken to the playlist.html template. On this template, up to the first 100 songs of the playlist are displayed. This is achieved by getting the user id and using the id argument for playlist_id, and getting the track names from the playlist.

### artist_top_songs

When an artist is found via search, or clicked on through a playlist or the user recommendation page, the user is taken to the artisttop.html template which displays the top 10 songs of said artist. This is done by finding the artist by plugging the id argument into the artist_id arguments of the Spotipy artist_top_tracks, and artist functions. Then we create a new list, loop through the artist tracks and append the track names to the list, and add the list to the context dictionary.

### artist_search

If a user enters an artist's name into the search bar, the app will give them a list of names that they can choose from. 

We start off by setting search_query to None by default and create an empty list. Then when a user submits a POST request we get the contents of the search bar and query for artists using the string that was entered with Spotipy's search function. If the search query returns artists, we create a set for seen names as there were times I would see duplicates (eg: when searching for Sleep Token I would get "Sleep Token" as well as "sleep token" as results). 

We then loop through the items in the artists object of our search query and if the name is not in our seen names set, we add the name to the set in lowercase, and append the artist to our unique artists list, which is then added to the context dictionary.

### statistics_view

The statistics_view renders the usertopsongs.html template as well as queries the user's top 50 songs and artists which the items of art added to variables that are passed to the context dictionary to be displayed.

### user_stats

Within the user_stats view, we query for the user's top 50 songs and artists. We then create two lists, "songs_by_artists" and "artist_genres". Looping through the top_songs_query we append the artists associated with each song to the "songs_by_artists" list. We then loop through the top_artists_query and append the genres associated with each artist to the artist_genres list.

With these lists we create two Pandas dataframes. The first using the artist_genres. We get the value_counts of the "genre" column, and find the percentage that the genre appeared within the user's top 50 artists. We then round it, get the top five, and create two lists, one for the genre labels, and one for the values.

The next dataframe is for the songs. With this dataframe we use the songs_by_artists list and get the value_counts of the "name" column. With the value_counts we take the top five and then split the results into two lists, one for song labels, another for song values.

Finally return a JsonResponse sending our genre_labels, genre_values, songs_by_artists, song_labels, song_values, artists, and songs to the front end.

## Urls.py

Contains all the url endpoints.

## Templates

### artistrec.html

Displays recommendations for songs based on recent artists the user has been listening to.

### artisttop.html

Displays the top 10 songs of the given artist (similar to when you go to an artist's page on the Spotify app).

### createplaylist.html

Create a new playlist for your Spotify account by filling in a playlist name, whether it is public or private, collaborative or not, and optionally a description. Once submitted, the app will create a playlist filled with recommendations based off of the user's recent listening trends.

### index.html

The front page of the app. Given four buttons to navigate the main functions of the app.

### layout.html

The layout is the skeleton of the styling for the app. This is where the navbar is located, as well as the script and style elements being linked. 

### playlist.html

Displays up to the first 100 songs in a given playlist.

### search.html

Displays results of the search query entered into the search bar. The result that closest matches the query will be listed at the top.

### userplaylists.html

Displays all the playlists created by the user. If clicked on will take them to playlist.html for that specific playlist.

### usertopsongs.html

This is the statistics page. Here you can see the user's top 50 most recent songs, top 50 most recent artists, a bar chart showing the top five artists by number of songs in user's top 50, and a pie chart of the user's top five genres.

## Static

### musicrec.js

The musicrec.js file handles the front end of the app. It starts by declaring variables getting elements from the DOM as well as setting "currentChart" and "jsonData" global variables for later use. 

Then we do a fetch request to /userstats/ to get the JsonResponse from our user_stats view. We save the data we get from this fetch request in the jsonData variable, and call a function we made later in the file with the data as well as 'bar' to create a bar chart for our songs by artists graph. 

Moving further down the file we get to a couple of on click event listeners. One for recentArtistsBtn and one for recentSongBtn. These will toggle display of every other element that could be within the display area to none, and toggle their display to block, as well as display the top 50 of the user's most recent songs or artists respectively. If pressed again, the display will be set back to none.

Next we get to the setChartType function. This function takes chartType as an argument. When called it will toggle the display of other elements that could be within the view area to none, and set the display of ctx (our chart variable) to block. Next it will destroy the currentChart if one exists, and create a new one with our makeChart function (which is declared next) which takes our jsonData, and chartType as arguments. This function gets called when our songsByArtistsBtn and genreBtn respectively are pressed (the onclick for these is inline in usertopsongs.html).

Finally we get to our makeChart function. This function utilizes the Chart.js library to display charts created dynamically with data received from our backend. This function takes two arguments, data, and type. Inside I added an if statement to check for which type of chart we want, we would want the data displayed to be different.

### styles.css

The stylesheet used in tandem with Bootstrap to style the app.

## .env

Within the .env file is where the client_id, and client_secret are held. These are then called within settings.py using os.getenv() to be able to be used within the rest of the program while being securely tucked away (obviously this is being uploaded for grading purposes). 

## requirements.txt

All of the required libraries and frameworks needed to run the app.

## Dockerfile

The Dockerfile needed to run the container. Created with the docker init command.

## compose.yaml

The compose file for Docker, needed for running the container, also created when running docker init command.

## package.json, package-lock.json, and node_modules

All three of these were installed along with Chart.js when installing via npm install command.
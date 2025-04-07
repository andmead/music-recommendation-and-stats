const chartContainer = document.getElementById('chartContainer');
const ctx = document.getElementById('myChart');
const recentSongBtn = document.getElementById('recentSongBtn');
const recentArtistsBtn = document.getElementById('recentArtistsBtn'); 
const userTopArtistsContainer = document.getElementById('userTopArtistsContainer');
const userTopSongsContainer = document.getElementById('userTopSongsContainer');
let currentChart;  
let jsonData;


fetch('/userstats/')
.then(response => {
  if (!response.ok) {
    throw new Error(`error status: ${response.status}`);
  }
  return response.json();
})
.then(data => {
  console.log(data);
  jsonData = data;
  makeChart(data, 'bar');
})
.catch(error => {
  console.error('Fetch error:', error);
});

recentArtistsBtn.addEventListener('click', () => {
  if (ctx.style.display === 'block' || userTopSongsContainer.style.display === 'block') {
    ctx.style.display = 'none';
    userTopSongsContainer.style.display = 'none';
  }

  if (userTopArtistsContainer.style.display !== 'block') {
    userTopArtistsContainer.style.display = 'block'
    userTopArtistsContainer.innerHTML = ``;
    for (let i = 0; i < jsonData.artists.length; i++) {
      const artist = jsonData.artists[i];
      console.log(artist)
      userTopArtistsContainer.innerHTML += `#${i + 1} - <a href="/top/${artist.id}">${artist.name}</a><br>`;
    }
  } else if (userTopArtistsContainer.style.display !== 'none') {
    userTopArtistsContainer.style.display = 'none'
  } 
});

recentSongBtn.addEventListener('click', () => {
  if (ctx.style.display === 'block' || userTopArtistsContainer.style.display === 'block') {
    ctx.style.display = 'none';
    userTopArtistsContainer.style.display = 'none';
  }

  if (userTopSongsContainer.style.display !== 'block') {
    userTopSongsContainer.style.display = 'block'
    userTopSongsContainer.innerHTML = ``;
    for (let i = 0; i < jsonData.songs.length; i++) {
      const song = jsonData.songs[i];
      console.log(song)

      userTopSongsContainer.innerHTML += `#${i + 1} - ${song.artists.map(artist => `<a href="/top/${artist.id}">${artist.name}</a>`).join(", ")} - ${song.name}<br>`;
    }
  } else if (userTopSongsContainer.style.display !== 'none') {
    userTopSongsContainer.style.display = 'none'
  } 
});


function setChartType(chartType) {
  if (userTopArtistsContainer.style.display === 'block' || userTopSongsContainer.style.display === 'block') {
    userTopArtistsContainer.style.display = 'none';
    userTopSongsContainer.style.display = 'none';
  }

  if (ctx.style.display === 'none') {
    ctx.style.display === 'block';
  }

  currentChart.destroy();
  makeChart(jsonData, chartType)
}


function makeChart(data, type) {
  if (type === 'bar') {
    currentChart = new Chart(ctx, {
      type: type,
      data: {
        labels: data.song_labels,
        datasets: [{
          label: 'Number of songs by artist in top recent songs',
          data: data.song_values,
          borderWidth: 1,
          backgroundColor: [
          'rgba(255, 99, 132, 0.7)',
					'rgba(75, 192, 192, 0.7)',
					'rgba(255, 205, 86, 0.7)',
					'rgba(54, 162, 235, 0.7)',
					'rgba(153, 102, 255, 0.7)',
        ],
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  else if (type === 'doughnut') {
    currentChart = new Chart(ctx, {
      type: type,
      data: {
        labels: data.genre_labels,
        datasets: [{
          label: 'Genre appearences in most recent songs',
          data: data.genre_values,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
      }
    });
  }
}

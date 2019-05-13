from simple_spotify.api import Spotify
from simple_spotify.authorization import ClientCredentialsFlow

from settings import CLIENT_ID, CLIENT_SECRET

"""
Get artist albums catalog data and album's artists name
"""


response = ClientCredentialsFlow.token_request(CLIENT_ID, CLIENT_SECRET)
auth = ClientCredentialsFlow(**response)
sp = Spotify(auth)

artist_id = '2dEKl1tM3JMwggawEuVISO'  # sora tob sakana

albums = sp.get_artist_albums(artist_id, country='JP', limit=50)

for album in albums.items:
    print(album.artists[0], album.name, album.release_date)

# Use pagination

print('--Use pagination--')

albums = sp.get_artist_albums(artist_id, country='JP', limit=1)
print(albums.items[0].name)

next_album = albums.get_next()
print(next_album.items[0].name)

prev_album = albums.get_previous()
print(prev_album.items[0].name)

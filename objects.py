class Artist:
    def __init__(self, artist_json):
        self.external_urls = artist_json['external_urls']
        self.followers = Followers(artist_json['followers'])
        self.genres = artist_json['genres']
        self.href = artist_json['href']
        self.artist_id = artist_json['id']
        self.images = [Image(img) for img in artist_json['images']]
        self.name = artist_json['name']
        self.popularity = artist_json['popularity']
        self.uri = artist_json['uri']

    def __str__(self):
        return self.name


class Followers:
    def __init__(self, followers):
        # href is always set to null as the Spotify Web API does not support it at the moment.
        self.href = followers['href'] if followers['href'] != 'null' else None
        self.total = followers['total']


class Image:
    def __init__(self, image):
        self.height = image['height']
        self.width = image['width']
        self.url = image['url']

    def __str__(self):
        return self.url

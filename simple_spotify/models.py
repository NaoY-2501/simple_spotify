from .consts import RESULT_TYPES


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

    @classmethod
    def raw_to_object(cls, raw):
        return cls(raw)

    def get_images(self):
        """
        Get image of artist as generator.
        :return: generator of Image object
        """
        for image in self.images:
            yield image


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


class SearchResult:
    def __init__(self, q, search_type, raw):
        self.q = q
        self.search_type = search_type
        self.raw = raw

    def __str__(self):
        return 'Query:{q} Result:{search_type}'.format(q=self.q, search_type=self.search_type)

    @property
    def albums(self):
        if 'album' in self.search_type:
            return SearchResultDetail(self.raw[RESULT_TYPES['album']])
        return None

    @property
    def artists(self):
        if 'artist' in self.search_type:
            return SearchResultDetail(self.raw[RESULT_TYPES['artist']])
        return None

    @property
    def playlists(self):
        if 'playlist' in self.search_type:
            return SearchResultDetail(self.raw[RESULT_TYPES['playlist']])
        return None

    @property
    def tracks(self):
        if 'track' in self.search_type:
            return SearchResultDetail(self.raw[RESULT_TYPES['track']])
        return None


# TODO: add next() and previous() as property.
class SearchResultDetail:
    def __init__(self, result_json):
        self.href = result_json['href']
        self.items = result_json['items']
        self.limit = result_json['limit']
        self.offset = result_json['offset']
        self.previous = result_json['previous']
        self.next = result_json['next']
        self.total = result_json['total']

    def __str__(self):
        return self.href

    def get_item(self):
        for item in self.items:
            yield item

from .consts import RESULT_TYPES


class Artist:
    def __init__(self, artist_json):
        self.raw = artist_json

    def __str__(self):
        return self.name

    @property
    def external_urls(self):
        return self.raw['external_urls']

    @property
    def href(self):
        return self.raw['href']

    @property
    def artist_id(self):
        return self.raw['id']

    @property
    def name(self):
        return self.raw['name']

    @property
    def obj_type(self):
        return self.raw['type']

    @property
    def uri(self):
        return self.raw['uri']

    @property
    def followers(self):
        if self.raw['followers']:
            followers = self.raw['followers']
            return followers['total']
        return None

    @property
    def followers_href(self):
        if self.raw['followers']:
            # href is always set to null as the Spotify Web API does not support it at the moment.
            followers = self.raw['followers']
            return followers['href'] if followers['href'] != 'null' else None
        return None

    @property
    def genres(self):
        if self.raw['genres']:
            return self.raw['genres']
        return None

    @property
    def images(self):
        images = []
        if self.raw['images']:
            for image in self.raw['images']:
                images.append(Image(image))
            return images
        return None

    @property
    def popularity(self):
        if self.raw['popularity']:
            return self.raw['popularity']
        return None

    @classmethod
    def raw_to_object(cls, raw):
        return cls(raw)


class Image:
    def __init__(self, image):
        self.height = image['height']
        self.width = image['width']
        self.url = image['url']

    def __str__(self):
        return self.url


class SearchResult:
    def __init__(self, q, search_type, result_json):
        self.q = q
        self.search_type = search_type
        self.raw = result_json

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
            return SearchResultDetail(self.raw[RESULT_TYPES['artist']], Artist)
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
    def __init__(self, result_json, klass=None):
        self.href = result_json['href']
        self.limit = result_json['limit']
        self.offset = result_json['offset']
        self.previous = result_json['previous']
        self.next = result_json['next']
        self.total = result_json['total']
        self.raw = result_json
        self.__klass = klass

    def __str__(self):
        return self.href

    @property
    def items(self):
        for item in self.raw['items']:
            if self.__klass:
                yield self.__klass(item)
            else:
                yield item

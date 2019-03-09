from .consts import RESULT_TYPES


class ObjectBase:
    def __init__(self, raw_json):
        self.raw = raw_json

    @classmethod
    def raw_to_object(cls, raw_json):
        return cls(raw_json)


class SimplifiedAlbum(ObjectBase):

    def __str__(self):
        return self.name

    @property
    def album_group(self):
        return self.raw['album_group']

    @property
    def album_type(self):
        return self.raw['album_type']

    @property
    def artists(self):
        converter = SimplifiedArtist.raw_to_object
        artists = []
        for artist in self.raw['artists']:
            artists.append(converter(artist))
        return artists

    @property
    def available_markets(self):
        return self.raw['available_markets']

    @property
    def external_urls(self):
        return self.raw['external_urls']

    @property
    def href(self):
        return self.raw['href']

    @property
    def album_id(self):
        return self.raw['id']

    @property
    def images(self):
        images = []
        converter = Image.convert_to_image
        for image in self.raw['images']:
            images.append(converter(image))
        return images

    @property
    def name(self):
        return self.raw['name']

    @property
    def release_date(self):
        return self.raw['release_date']

    @property
    def release_date_precision(self):
        return self.raw['release_date_precision']

    @property
    def restrictions(self):
        return self.raw['restrictions']

    @property
    def obj_type(self):
        return self.raw['type']

    @property
    def uri(self):
        return self.raw['uri']


class Album(SimplifiedAlbum):

    @property
    def copyrights(self):
        copyrights = []
        converter = CopyRight.convert_to_copyright
        for right in self.raw['copyrights']:
            copyrights.append(converter(right))
        return copyrights

    @property
    def external_uris(self):
        return self.raw['external_uris']

    @property
    def external_urls(self):
        return self.raw['external_urls']

    @property
    def label(self):
        return self.raw['label']

    @property
    def popularity(self):
        return self.raw['popularity']

    @property
    def tracks(self):
        # return array of simplified tracks inside paging object
        # TODO: return list of SimplifiedTrack after implement SimplifiedTrack Class.
        return self.raw['tracks']


class SimplifiedArtist(ObjectBase):

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


class Artist(SimplifiedArtist):

    @property
    def followers(self):
        followers = self.raw['followers']
        return followers['total']

    @property
    def followers_href(self):
        # href is always set to null as the Spotify Web API does not support it at the moment.
        followers = self.raw['followers']
        return followers['href'] if followers['href'] != 'null' else None

    @property
    def genres(self):
        return self.raw['genres']

    @property
    def images(self):
        images = []
        converter = Image.convert_to_image
        for image in self.raw['images']:
            images.append(converter(image))
        return images

    @property
    def popularity(self):
        return self.raw['popularity']


class SimplifiedTrack(ObjectBase):

    def __str__(self):
        return self.raw['name']

    @property
    def artists(self):
        converter = SimplifiedArtist.raw_to_object
        artists = []
        for artist in self.raw['artists']:
            artists.append(converter(artist))
        return artists



class CopyRight:
    def __init__(self, raw_copyright):
        self.text = raw_copyright['text']
        self.copyright_type = raw_copyright['type']

    @classmethod
    def convert_to_copyright(cls, raw_copyright):
        return cls(raw_copyright)


class Image:
    def __init__(self, image):
        self.height = image['height']
        self.width = image['width']
        self.url = image['url']

    def __str__(self):
        return self.url

    @classmethod
    def convert_to_image(cls, raw_json):
        return cls(raw_json)


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

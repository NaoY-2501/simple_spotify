from .consts import RESULT_TYPES


class ObjectBase:
    def __init__(self, raw_json):
        self.raw = raw_json

    @property
    def external_urls(self):
        return self.raw['external_urls']

    @property
    def href(self):
        return self.raw['href']

    @property
    def name(self):
        return self.raw['name']

    @property
    def obj_type(self):
        return self.raw['type']

    @property
    def uri(self):
        return self.raw['uri']

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
    def release_date(self):
        return self.raw['release_date']

    @property
    def release_date_precision(self):
        return self.raw['release_date_precision']

    @property
    def restrictions(self):
        return self.raw['restrictions']


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
        return ExternalURL(self.raw['external_urls'])

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
    def artist_id(self):
        return self.raw['id']


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

    @property
    def available_markets(self):
        return self.raw['available_markets']

    @property
    def disc_number(self):
        return self.raw['disc_number']

    @property
    def duration_ms(self):
        return self.raw['duration_ms']

    @property
    def explicit(self):
        return self.raw['explicit']

    @property
    def track_id(self):
        return self.raw['id']

    @property
    def is_playable(self):
        return self.raw['is_playable']

    @property
    def linked_from(self):
        value = self.raw.get('linked_from')
        if value:
            return TrackLink(value)
        return value

    @property
    def restrictions(self):
        value = self.raw.get('restricitons')
        if value:
            return Restrictions(value)
        return value

    @property
    def name(self):
        return self.raw['name']

    @property
    def preview_url(self):
        return self.raw['preview_url']

    @property
    def track_number(self):
        return self.raw['track_number']

    @property
    def is_local(self):
        return self.raw['is_local']


class Track(SimplifiedTrack):

    @property
    def album(self):
        return SimplifiedAlbum(self.raw['album'])

    @property
    def external_ids(self):
        return ExternalID(self.raw['external_ids'])

    @property
    def popularity(self):
        return self.raw['popularity']


class CopyRight:
    def __init__(self, raw_copyright):
        self.text = raw_copyright['text']
        self.copyright_type = raw_copyright['type']

    @classmethod
    def convert_to_copyright(cls, raw_copyright):
        return cls(raw_copyright)


class ExternalID:
    def __init__(self, raw_external_id):
        self.identifier_type = list(raw_external_id.keys())[0]
        self.identifier = list(raw_external_id.values())[0]

    def __str__(self):
        return '{type}:{id}'.format(
            type=self.identifier_type,
            id=self.identifier
        )


class ExternalURL:
    def __init__(self, raw_external_url):
        self.url = raw_external_url['spotify']

    def __str__(self):
        return self.url


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


class Restrictions:
    def __init__(self, raw_restrictions):
        self.raw = raw_restrictions['restrictions']['reason']


class TrackLink:
    def __init__(self, raw_track_link):
        self.external_url = ExternalURL(raw_track_link['external_url'])
        self.href = raw_track_link['href']
        self.link_id = raw_track_link['id']
        self.obj_type = raw_track_link['type']
        self.uri = raw_track_link.get['uri']


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

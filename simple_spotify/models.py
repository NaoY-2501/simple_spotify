import datetime

from .consts import PITCH_CLASS
from .util import http_request


class ObjectBase:
    def __init__(self, raw_json):
        self.raw = raw_json

    @property
    def as_dict(self):
        return self.raw

    @classmethod
    def to_object(cls, raw_json):
        return cls(raw_json)


class SimplifiedObjectBase(ObjectBase):

    @property
    def external_urls(self):
        return self.raw['external_urls']['spotify']

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


class SimplifiedAlbum(SimplifiedObjectBase):

    def __str__(self):
        return self.name

    @property
    def album_group(self):
        return self.raw.get('album_group')

    @property
    def album_type(self):
        return self.raw['album_type']

    @property
    def artists(self):
        converter = SimplifiedArtist.to_object
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

    def __init__(self, raw_json, auth):
        super(Album, self).__init__(raw_json)
        self.auth = auth
        self.tracks = Paging(self.raw['tracks'], SimplifiedTrack, self.auth)

    @property
    def copyrights(self):
        copyrights = []
        converter = CopyRight.convert_to_copyright
        for right in self.raw['copyrights']:
            copyrights.append(converter(right))
        return copyrights

    @property
    def external_ids(self):
        return ExternalID(self.raw['external_ids'])

    @property
    def label(self):
        return self.raw['label']

    @property
    def popularity(self):
        return self.raw['popularity']


class AudioFeature(ObjectBase):

    @property
    def duration_ms(self):
        return self.raw['duration_ms']

    @property
    def key(self):
        return self.raw['key']

    @property
    def mode(self):
        return self.raw['mode']

    @property
    def time_signature(self):
        return self.raw['time_signature']

    @property
    def acousticness(self):
        return self.raw['acousticness']

    @property
    def danceability(self):
        return self.raw['danceability']

    @property
    def energy(self):
        return self.raw['energy']

    @property
    def instrumentalness(self):
        return self.raw['instrumentalness']

    @property
    def liveness(self):
        return self.raw['liveness']

    @property
    def loudness(self):
        return self.raw['loudness']

    @property
    def speechiness(self):
        return self.raw['speechiness']

    @property
    def valence(self):
        return self.raw['valence']

    @property
    def tempo(self):
        return self.raw['tempo']

    @property
    def track_id(self):
        return self.raw['id']

    @property
    def uri(self):
        return self.raw['uri']

    @property
    def track_href(self):
        return self.raw['track_href']

    @property
    def analysis_url(self):
        return self.raw['analysis_url']

    @property
    def obj_type(self):
        return self.raw['type']

    @property
    def key_name(self):
        return PITCH_CLASS.get(self.key)

    @property
    def duration_s(self):
        return self.duration_ms/1000

    @property
    def duration_min(self):
        return str(datetime.timedelta(seconds=self.duration_s))


class SimplifiedArtist(SimplifiedObjectBase):

    def __str__(self):
        return self.name

    @property
    def artist_id(self):
        return self.raw['id']


class Artist(SimplifiedArtist):

    @property
    def followers(self):
        # followers also has href but does not implement.
        # Because, href is always set to null as the Spotify Web API does not support it at the moment.
        return self.raw['followers']['total']

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


class SimplifiedTrack(SimplifiedObjectBase):

    def __str__(self):
        return self.raw['name']

    @property
    def artists(self):
        converter = SimplifiedArtist.to_object
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
        self.external_url = raw_track_link['external_url']['spotify']
        self.href = raw_track_link['href']
        self.link_id = raw_track_link['id']
        self.obj_type = raw_track_link['type']
        self.uri = raw_track_link.get['uri']


class SearchResult:
    def __init__(self, q, search_type, result_json, auth):
        self.q = q
        self.search_type = search_type
        self.raw = result_json
        self.auth = auth
        self.albums = CustomPaging(
            self.raw,
            SimplifiedAlbum,
            self.auth,
            'albums') if 'album' in self.search_type else None
        self.artists = CustomPaging(
            self.raw,
            Artist,
            self.auth,
            'artists') if 'artist' in self.search_type else None
        self.playlists = CustomPaging(
            self.raw,
            SimplifiedPlaylist,
            self.auth,
            'playlists') if 'playlist' in self.search_type else None
        self.tracks = CustomPaging(
            self.raw,
            Track,
            self.auth,
            'tracks') if 'track' in self.search_type else None

    def __str__(self):
        return 'Query:{q} Result:{search_type}'.format(q=self.q, search_type=self.search_type)


class PagingBase:
    def __init__(self, klass, auth):
        self.klass = klass
        self.auth = auth

    def __paging__(self, url):
        response = http_request(self.auth, url)
        page = Paging(response, self.klass, self.auth)
        self.href = response['href']
        self.items = self.__items__(response)
        self.next = response['next']
        self.previous = response['previous']
        return page

    def __items__(self, response):
        if response:
            return [self.klass.to_object(item) for item in response['items']]
        return None

    def get_next(self):
        if self.next:
            return self.__paging__(self.next)
        return None


class Paging(PagingBase):
    def __init__(self, raw_json, klass, auth):
        super(Paging, self).__init__(klass, auth)
        self.href = raw_json['href']
        self.items = self.__items__(raw_json)
        self.limit = raw_json['limit']
        self.next = raw_json['next']
        self.offset = raw_json['offset']
        self.previous = raw_json['previous']
        self.total = raw_json['total']

    def get_previous(self):
        if self.previous:
            return self.__paging__(self.previous)
        return None


class CustomPaging(PagingBase):
    def __init__(self, raw_json, klass, auth, key):
        super(CustomPaging, self).__init__(klass, auth)
        self.message = raw_json.get('message', None)
        self.key = key
        self.raw = raw_json[key]
        self.href = self.raw['href']
        self.items = self.__items__(self.raw)
        self.limit = self.raw['limit']
        self.next = self.raw['next']
        self.offset = self.raw['offset']
        self.previous = self.raw['previous']
        self.total = self.raw['total']

    def __paging__(self, url):
        response = http_request(self.auth, url)
        page = CustomPaging(response, self.klass, self.auth, self.key)
        self.href = response[self.key]['href']
        self.items = self.__items__(response[self.key])
        self.next = response[self.key]['next']
        self.previous = response[self.key]['previous']
        return page

    def get_previous(self):
        if self.previous:
            return self.__paging__(self.previous)
        return None


class CursorBasedPaging(PagingBase):
    def __init__(self, raw_json, klass, auth, key):
        super(CursorBasedPaging, self).__init__(klass, auth)
        self.key = key
        self.raw = raw_json[key]
        self.href = self.raw['href']
        self.items = self.__items__(self.raw)
        self.limit = self.raw['limit']
        self.next = self.raw['next']
        self.cursor = {'after': self.raw['cursors']['after']}
        self.total = self.raw['total']

    def __paging__(self, url):
        response = http_request(self.auth, url)
        page = CustomPaging(response, self.klass, self.auth, self.key)
        self.href = response[self.key]['href']
        self.items = self.__items__(response[self.key])
        self.next = response[self.key]['next']
        self.previous = response[self.key]['previous']
        return page


class UserBase(ObjectBase):

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.raw['display_name']

    @property
    def external_urls(self):
        return self.raw['external_urls']['spotify']

    def followers(self):
        # followers also has href but does not implement.
        # Because, href is always set to null as the Spotify Web API does not support it at the moment.
        return self.raw['followers']['total']

    @property
    def href(self):
        return self.raw['href']

    @property
    def user_id(self):
        return self.raw['id']

    @property
    def images(self):
        images = []
        converter = Image.convert_to_image
        for image in self.raw['images']:
            images.append(converter(image))
        return images

    @property
    def obj_type(self):
        return self.raw['type']

    @property
    def uri(self):
        return self.raw['uri']


class PrivateUser(UserBase):

    @property
    def birthdate(self):
        return self.raw.get('birthdate', None)

    @property
    def country(self):
        return self.raw.get('country', None)

    @property
    def display_name(self):
        return self.raw['display_name']

    @property
    def email(self):
        return self.raw.get('email', None)

    @property
    def product(self):
        return self.raw.get('product', None)


class PublicUser(UserBase):
    pass


class SimplifiedPlaylist(SimplifiedObjectBase):

    def __str__(self):
        return self.playlist_id

    @property
    def collaborative(self):
        return self.raw['collaborative']

    @property
    def playlist_id(self):
        return self.raw['id']

    @property
    def images(self):
        images = []
        converter = Image.convert_to_image
        for image in self.raw['images']:
            images.append(converter(image))
        return images

    @property
    def owner(self):
        return PublicUser(self.raw['owner'])

    @property
    def public(self):
        return self.raw['public']

    @property
    def snapshot_id(self):
        return self.raw['snapshot_id']

    @property
    def tracks(self):
        return {
            'href': self.raw['tracks']['href'],
            'total': self.raw['tracks']['total']
        }


class Playlist(SimplifiedPlaylist):

    def __str__(self):
        return self.name

    @property
    def description(self):
        return self.raw['description']

    def followers(self):
        # followers also has href but does not implement.
        # Because, href is always set to null as the Spotify Web API does not support it at the moment.
        return self.raw['followers']['total']

    @property
    def name(self):
        return self.raw['name']


class AudioAnalysis(ObjectBase):
    @property
    def bars(self):
        return [TimeInterval(bar) for bar in self.raw['bars']]

    @property
    def beats(self):
        return [TimeInterval(beat) for beat in self.raw['beats']]

    @property
    def sections(self):
        return [Section(section) for section in self.raw['sections']]

    @property
    def segments(self):
        return [Segment(segment) for segment in self.raw['segments']]

    @property
    def tatums(self):
        return [TimeInterval(tatum) for tatum in self.raw['tatums']]


class TimeInterval(ObjectBase):
    @property
    def start(self):
        return self.raw['start']

    @property
    def duration(self):
        return self.raw['duration']

    @property
    def confidence(self):
        return self.raw['confidence']


class Section(ObjectBase):
    @property
    def start(self):
        return self.raw['start']

    @property
    def duration(self):
        return self.raw['duration']

    @property
    def confidence(self):
        return self.raw['confidence']

    @property
    def loudness(self):
        return self.raw['loudness']

    @property
    def tempo(self):
        return self.raw['tempo']

    @property
    def tempo_confidence(self):
        return self.raw['tempo_confidence']

    @property
    def key(self):
        return self.raw['key']

    @property
    def key_str(self):
        return PITCH_CLASS.get(self.key)

    @property
    def key_confidence(self):
        return self.raw['key_confidence']

    @property
    def mode(self):
        return self.raw['mode']

    @property
    def mode_confidence(self):
        return self.raw['mode_confidence']

    @property
    def time_signature(self):
        return self.raw['time_signature']

    @property
    def time_signature_confidence(self):
        return self.raw['time_signature_confidence']


class Segment(ObjectBase):
    @property
    def start(self):
        return self.raw['start']

    @property
    def duration(self):
        return self.raw['duration']

    @property
    def confidence(self):
        return self.raw['confidence']

    @property
    def loudness_start(self):
        return self.raw['loudness_start']

    @property
    def loudness_max(self):
        return self.raw['loudness_max']

    @property
    def loudness_max_time(self):
        return self.raw['loudness_max_time']

    @property
    def loudness_end(self):
        return self.raw['loudness_end']

    @property
    def pitches(self):
        return self.raw['pitches']

    @property
    def timbre(self):
        return self.raw['timbre']


class Category(ObjectBase):
    def __str__(self):
        return self.name

    @property
    def href(self):
        return self.raw['href']

    @property
    def icons(self):
        icons = []
        converter = Image.convert_to_image
        for icon in self.raw['icons']:
            icons.append(converter(icon))
        return icons

    @property
    def category_id(self):
        return self.raw['id']

    @property
    def name(self):
        return self.raw['name']


class RecommendationsResponse(ObjectBase):
    @property
    def seeds(self):
        return [seed for seed in self.raw['seeds']]

    @property
    def tracks(self):
        return [SimplifiedTrack.to_object(track) for track in self.raw['tracks']]


class RecommendationSeed(ObjectBase):
    @property
    def after_filtering_size(self):
        return self.raw['afterFilteringSize']

    @property
    def after_relinking_size(self):
        return self.raw['afterRelinkingSize']

    @property
    def href(self):
        return self.raw['href']

    @property
    def seed_id(self):
        return self.raw['id']

    @property
    def initial_pool_size(self):
        return self.raw['initialPoolSize']

    @property
    def seed_type(self):
        return self.raw['type']


class SavedAlbum(ObjectBase):
    @property
    def added_at(self):
        return self.raw['added_at']

    @property
    def album(self):
        return Album(self.raw['album'])


class SavedTrack(ObjectBase):
    @property
    def added_at(self):
        return self.raw['added_at']

    @property
    def track(self):
        return Track(self.raw['track'])

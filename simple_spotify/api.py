import urllib.parse

from .consts import SEARCH_TYPES
from .decorators import id_validation, ids_validation, token_refresh
from .errors import QueryValidationError
from .models import Album,SimplifiedAlbum, Artist, SimplifiedTrack, Track, AudioFeature, SearchResult, Paging
from .util import get_response


class SpotifyBase:
    def __init__(self, authorization):
        self.authorization = authorization

    @classmethod
    def make_full_url(cls, endpoint, data):
        full_url = '{endpoint}?{data}'.format(
            endpoint=endpoint,
            data=data
        )
        return full_url


class Spotify(SpotifyBase):

    @id_validation
    @token_refresh
    def album(self, album_id):
        """
        Get album information
        Endpoint: GET https://api.spotify.com/v1/albums/{id}
        :param album_id:
        :return:Album object
        """
        endpoint = 'https://api.spotify.com/v1/albums/{id}'.format(
            id=album_id
        )
        response = get_response(self.authorization, endpoint)
        result = Album(response, self.authorization)
        return result

    @id_validation
    @token_refresh
    def albums_tracks(self, album_id, limit=20, offset=0, market=None):
        """
        Get tracks which is contained album
        :param album_id:
        :param limit: maximum number of results to return. Default 20. min 1, max 50.
        :param offset: The index of the first result to return. Default 0. max 10,000.
        :param market: ISO 3166-1 alpha-2 country code
        :return: paging object with track objects
        """
        endpoint = 'https://api.spotify.com/v1/albums/{id}/tracks'.format(
            id=album_id
        )
        # validate limit
        if not isinstance(limit, int):
            raise QueryValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        # validate offset
        if not isinstance(offset, int):
            raise QueryValidationError('offset must be int.')
        if offset > 10000:
            offset = 10000

        queries = {
            'limit': limit,
            'offset': offset
        }
        if market:
            queries['market'] = market

        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        return Paging(response, SimplifiedTrack, self.authorization)

    @ids_validation
    @token_refresh
    def albums(self, album_ids):
        """
        Get several albums information.
        Endpoint:GET https://api.spotify.com/v1/albums
        :param album_ids: list of album id. Maximum : 50 IDs
        :return: list of album objects
        """
        endpoint = 'https://api.spotify.com/v1/albums'

        query = {
            'ids': ','.join(album_ids)
        }

        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        converter = Album.to_object
        results = []
        for result in response['albums']:
            results.append(converter(result))
        return results

    @id_validation
    @token_refresh
    def artist(self, artist_id):
        """
        Get artist information.
        Endpoint:GET https://api.spotify.com/v1/artists/{id}
        :param artist_id:
        :return: Artist object
        """
        endpoint = 'https://api.spotify.com/v1/artists/{id}'.format(
            id=artist_id
        )
        response = get_response(self.authorization, endpoint)
        result = Artist(response)
        return result

    @ids_validation
    @token_refresh
    def artists(self, artist_ids):
        """
        Get several artists information.
        Endpoint:GET https://api.spotify.com/v1/artists
        :param artist_ids: list of artist id. Maximum : 50 IDs
        :return: list of Artist objects
        """
        endpoint = 'https://api.spotify.com/v1/artists'

        query = {
            'ids': ','.join(artist_ids)
        }

        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        converter = Artist.to_object
        results = []
        for result in response['artists']:
            results.append(converter(result))
        return results

    @id_validation
    @token_refresh
    def artist_albums(self, artist_id, limit=20, offset=0, country=None):
        """
        Get information about artist's albums
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/albums
        :param artist_id:
        :param limit: maximum number of results to return. Default 20. min 1, max 50.
        :param offset: The index of the first result to return. Default 0. max 10,000.
        :param country: ISO 3166-1 alpha-2 country code
        :return: paging object with SimplifiedAlbum objects.
        """
        endpoint = 'https://api.spotify.com/v1/artists/{id}/albums'.format(
            id=artist_id
        )
        # validate limit
        if not isinstance(limit, int):
            raise QueryValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        # validate offset
        if not isinstance(offset, int):
            raise QueryValidationError('offset must be int.')
        if offset > 10000:
            offset = 10000

        queries = {
            'limit': limit,
            'offset': offset
        }
        if country:
            queries['market'] = country

        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        return Paging(response, SimplifiedAlbum, self.authorization)

    @id_validation
    @token_refresh
    def related_artists(self, artist_id):
        """
        Get information about 20 related artists to a given artist.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/related-artists
        :param artist_id:
        :return: list of Artist objects
        """
        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}/related-artists'.format(
            artist_id=artist_id
        )
        response = get_response(self.authorization, endpoint)
        converter = Artist.to_object
        results = []
        for result in response['artists']:
            results.append(converter(result))
        return results

    @id_validation
    @token_refresh
    def artist_top_tracks(self, artist_id, county_code=None):
        """
        Get information about an artist's top tracks.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/top-tracks
        :param artist_id:
        :param county_code: ISO 3166-1 alpha-2 country code
        :return: list of Track objects
        """
        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'.format(
            artist_id=artist_id
        )
        # coutry_code validation
        if not county_code:
            raise QueryValidationError('country_code is required parameter.')
        if not isinstance(county_code, str):
            raise QueryValidationError('country_code must be str.')

        query = {
            'country': county_code
        }
        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        converter = Track.to_object
        results = []
        for result in response['tracks']:
            results.append(converter(result))
        return results

    @id_validation
    @token_refresh
    def track(self, track_id):
        """
        Get track information.
        Endpoint: GET https://api.spotify.com/v1/tracks/{id}
        :param track_id:
        :return: Track object
        """
        endpoint = 'https://api.spotify.com/v1/tracks/{track_id}'.format(
            track_id=track_id
        )
        response = get_response(self.authorization, endpoint)
        result = Track(response)
        return result

    @id_validation
    @token_refresh
    def audio_feature(self, track_id):
        """
        Get audio feature for track.
        :param track_id:
        :return: AudioFeature object
        """
        endpoint = 'https://api.spotify.com/v1/audio-features/{track_id}'.format(
            track_id=track_id
        )
        response = get_response(self.authorization, endpoint)
        result = AudioFeature(response)
        return result

    @token_refresh
    def search(self, q='', search_types=SEARCH_TYPES, market=None, limit=20, offset=0):
        """
        Get information about artists, albums, tracks, playlist with match a keyword string.
        :param q: search keyword
        :param search_types: iterable object contains search type. Default is ['album', 'artist', 'playlist', 'track'].
        :param market: ISO 3166-1 alpha-2 country code
        :param limit: maximum number of results to return. Default 20. min 1, max 50.
        :param offset: The index of the first result to return. Default 0. max 10,000.
        :return: SearchResult objects or json format dict when raw is True.
        """
        endpoint = 'https://api.spotify.com/v1/search'

        # validate query
        if not isinstance(q, str):
            raise QueryValidationError('Query must be str.')
        if not q:
            raise QueryValidationError('Query is empty.')

        # validate search_types
        if not hasattr(search_types, '__iter__'):
            raise QueryValidationError('search_types must be iterable.')

        for t in search_types:
            try:
                if t.lower() not in SEARCH_TYPES:
                    raise QueryValidationError('{} is invalid search type.'.format(t))
            except AttributeError:
                raise AttributeError('Invalid type object in search_types. search_types must be list of string')

        # validate limit
        if not isinstance(limit, int):
            raise QueryValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        # validate offset
        if not isinstance(offset, int):
            raise QueryValidationError('offset must be int.')
        if offset > 10000:
            offset = 10000

        typestring = ','.join([t.lower() for t in search_types])

        queries = {
            'q': q,
            'type': typestring,
            'limit': limit,
            'offset': offset
        }
        if market:
            queries['market'] = market

        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        results = SearchResult(q, search_types, response, self.authorization)
        return results

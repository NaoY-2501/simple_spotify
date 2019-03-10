import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from .consts import SEARCH_TYPES
from .errors import SpotifyHTTPError, SpotifyQueryError
from .models import Album, Artist, Track, SearchResult, SearchResultDetail


class SpotifyBase:
    def __init__(self, client_id, client_secret):
        self.access_token = self.__auth__(client_id, client_secret)['access_token']
        self.header_params = {'Authorization': 'Bearer {}'.format(self.access_token)}

    def __auth__(self, client_id, client_secret):
        endpoint = 'https://accounts.spotify.com/api/token'

        base64string = base64.encodebytes('{client_id}:{client_secret}'.format(
            client_id=client_id,
            client_secret=client_secret
        ).encode('utf-8'))

        headers = {'Authorization': 'Basic {base64string}'.format(
            base64string=base64string.decode('utf-8')
        ).replace('\n', '')}  # trailing \n in base64string

        body = {'grant_type': 'client_credentials'}

        data = urllib.parse.urlencode(body).encode('ascii')
        req = urllib.request.Request(endpoint, data, headers)
        try:
            with urllib.request.urlopen(req) as res:
                # keys:access_token, token_type, Bearer, expires_in, scope
                json_res = self.get_json_res(res)
            return json_res
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

    @classmethod
    def get_json_res(cls, res):
        return json.loads(res.read().decode('utf-8'))


class Spotify(SpotifyBase):

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
        req = urllib.request.Request(endpoint, headers=self.header_params)
        try:
            with urllib.request.urlopen(req) as res:
                json_res = self.get_json_res(res)
                result = Album(json_res)
                return result
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

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
        req = urllib.request.Request(endpoint, headers=self.header_params)
        try:
            with urllib.request.urlopen(req) as res:
                json_res = self.get_json_res(res)
                result = Artist(json_res)
                return result
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

    def artists(self, artist_ids):
        """
        Get several artists information.
        Endpoint:GET https://api.spotify.com/v1/artists
        :param artist_ids: list of artist id
        :return: iterator of Artist objects
        """

        # query validation
        if not isinstance(artist_ids, list):
            raise SpotifyQueryError('artist ids must be list.')
        for each in artist_ids:
            if not isinstance(each, str):
                raise SpotifyQueryError('artist id must be str.')

        endpoint = 'https://api.spotify.com/v1/artists'
        values = {
            'ids': ','.join(artist_ids)
        }

        data = urllib.parse.urlencode(values)
        full_url = endpoint + '?' + data
        req = urllib.request.Request(full_url, headers=self.header_params)
        try:
            with urllib.request.urlopen(req) as res:
                json_res = self.get_json_res(res)
                converter = Artist.raw_to_object
                for result in json_res['artists']:
                    yield converter(result)
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

    def related_artists(self, artist_id):
        """
        Get information about 20 related artists to a given artist.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/related-artists
        :param artist_id:
        :return: List of Artist objects
        """
        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}/related-artists'.format(
            artist_id=artist_id
        )
        req = urllib.request.Request(endpoint, headers=self.header_params)

        try:
            with urllib.request.urlopen(req) as res:
                json_res = self.get_json_res(res)
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

        converter = Artist.raw_to_object
        results = []
        for each in json_res['artists']:
            results.append(converter(each))
        return results

    def artist_top_tracks(self, artist_id, county_code=None):
        """
        Get information about an artist's top tracks.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/top-tracks
        :param artist_id:
        :param county_code: ISO 3166-1 alpha-2 country code
        :return: iterator of Track objects
        """
        # coutry_code validation
        if not county_code:
            raise SpotifyQueryError('country_code is required parameter.')
        if not isinstance(county_code, str):
            raise SpotifyQueryError('country_code must be str.')

        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'.format(
            artist_id=artist_id
        )
        values = {
            'country': county_code
        }
        data = urllib.parse.urlencode(values)
        full_url = endpoint + '?' + data
        req = urllib.request.Request(full_url, headers=self.header_params)
        try:
            with urllib.request.urlopen(req) as res:
                json_res = self.get_json_res(res)
                converter = Track.raw_to_object
                for result in json_res['tracks']:
                    yield converter(result)
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

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
        req = urllib.request.Request(endpoint, headers=self.header_params)
        try:
            with urllib.request.urlopen(req) as res:
                json_res = self.get_json_res(res)
                result = Track(json_res)
                return result
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

    def paging(self, href):
        """
        paging for search result
        :param href: link to prev/next page
        :return: SearchResultDetail object or json format dict when raw is True.
        """
        if href:
            req = urllib.request.Request(href, headers=self.header_params)

            try:
                with urllib.request.urlopen(req) as res:
                    json_res = self.get_json_res(res)
            except urllib.error.HTTPError as e:
                raise SpotifyHTTPError(e.reason, e.code)

            key = list(json_res.keys())[0]
            return SearchResultDetail(json_res[key])
        return None

    def search(self, q='', search_type=SEARCH_TYPES, market=None, limit=20, offset=0):
        """
        Get information about artists, albums, tracks, playlist with match a keyword string.
        :param q: search keyword
        :param search_type: list of search type. Default is [album, artist, playlist, track].
        :param market: ISO 3166-1 alpha-2 country code
        :param limit: maximum number of results to return. Default 20. min 1, max 50.
        :param offset: The index of the first result to return. Default 0. max 10,000.
        :return: SearchResult objects or json format dict when raw is True.
        """
        endpoint = 'https://api.spotify.com/v1/search'

        # query validation
        if not isinstance(q, str):
            raise SpotifyQueryError('Query must be str.')
        if not q:
            raise SpotifyQueryError('Query is empty.')

        # convert tuple to list.
        if isinstance(search_type, tuple):
            search_type = list(search_type)
        # type validation
        if not isinstance(search_type, list):
            raise SpotifyQueryError('search_type must be list.')

        for t in search_type:
            try:
                if t.lower() not in SEARCH_TYPES:
                    raise SpotifyQueryError('{} is invalid search type.'.format(t))
            except AttributeError:
                raise AttributeError('Invalid type object in search_type. search_type must be list of string')

        # limit validation
        if not isinstance(limit, int):
            raise SpotifyQueryError('limit must be int.')
        if limit > 50:
            limit = 50

        # offset validation
        if not isinstance(offset, int):
            raise SpotifyQueryError('offset must be int.')
        if offset > 10000:
            offset = 10000

        typestring = ','.join([t.lower() for t in search_type])

        values = {
            'q': q,
            'type': typestring,
            'limit': limit,
            'offset': offset
        }
        if market:
            values['market'] = market

        data = urllib.parse.urlencode(values)
        full_url = endpoint + '?' + data
        req = urllib.request.Request(full_url, headers=self.header_params)

        try:
            with urllib.request.urlopen(req) as res:
                json_res = self.get_json_res(res)
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

        results = SearchResult(q, search_type, json_res)
        return results

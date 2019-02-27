import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from .consts import SEARCH_TYPES
from .errors import SpotifyHTTPError, SpotifySearchTypeError
from .models import Artist, SearchResult, SearchResultDetail


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

        bodys = {'grant_type': 'client_credentials'}

        data = urllib.parse.urlencode(bodys).encode('ascii')
        req = urllib.request.Request(endpoint, data, headers)
        try:
            with urllib.request.urlopen(req) as res:
                # keys:access_token, token_type, Bearer, expires_in, scope
                json_res = json.loads(res.read().decode('utf-8'))
            return json_res
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

    @classmethod
    def get_json_res(cls, res):
        return json.loads(res.read().decode('utf-8'))


class Spotify(SpotifyBase):
    def artist(self, artist_id, raw=False):
        """
        Get artist information.
        Endpoint:GET https://api.spotify.com/v1/artists/{id}
        :param artist_id:
        :param raw: If you want to get response as json format, specify to True.
        :return: Artist object
        """
        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}'.format(
            artist_id=artist_id
        )
        req = urllib.request.Request(endpoint, headers=self.header_params)
        try:
            with urllib.request.urlopen(req) as res:
                json_res = self.get_json_res(res)
                if raw:
                    return json_res
                else:
                    return Artist(json_res)
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

    def related_artists(self, artist_id, raw=False):
        """
        Get information about 20 related artists to a given artist.
        :param artist_id:
        :param raw: If you want to get response as json format, specify to True.
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

        if raw:
            return json_res
        else:
            converter = Artist.raw_to_object
            results = []
            for each in json_res['artists']:
                results.append(converter(each))
            return results

    def search(self, q, search_type, market=None, limit=20, offset=0, raw=False):
        """
        Get information about artists, albums, tracks, playlist with match a keyword string.
        :param q: search keyword
        :param search_type: list of search type(album, artist, playlist, track)
        :param market: ISO 3166-1 alpha-2 country code
        :param limit: maximum number of results to return. Default 20. min 1, max 50.
        :param offset: The index of the first result to return. Default 0. max 10,000.
        :param raw: If you want to get response as json format, specify to True.
        :return: SearchResult objects
        """
        endpoint = 'https://api.spotify.com/v1/search'

        # type validation
        for t in search_type:
            try:
                if t.lower() not in SEARCH_TYPES:
                    raise SpotifySearchTypeError(t)
            except AttributeError:
                raise AttributeError('Invalid type object in search_type. search_type must be list of string')

        # limit validation
        if not isinstance(limit, int):
            raise TypeError('limit must be int.')
        if limit > 50:
            limit = 50

        # offset validation
        if not isinstance(offset, int):
            raise TypeError('offset must be int.')
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

        search_results = SearchResult(q, search_type, json_res)

        if raw:
            return json_res
        return search_results

    def paging(self, href, raw=False):
        """
        paging for search result
        :param href: link to prev/next page
        :param raw: If you want to get response as json format, specify to True.
        :return: SearchResultDetail object
        """
        if href:
            req = urllib.request.Request(href, headers=self.header_params)

            try:
                with urllib.request.urlopen(req) as res:
                    json_res = self.get_json_res(res)
            except urllib.error.HTTPError as e:
                raise SpotifyHTTPError(e.reason, e.code)

            if raw:
                return json_res
            key = list(json_res.keys())[0]
            return SearchResultDetail(json_res[key])
        return None

import json
import urllib.error
import urllib.parse
import urllib.request

from .consts import SEARCH_TYPES
from .errors import HTTPError, QueryValidationError
from .models import Album, Artist, Track, AudioFeature, SearchResult, SearchResultDetail


class SpotifyBase:
    def __init__(self, authorization):
        self.authorization = authorization

    def get_response(self, url, data=None):
        req = urllib.request.Request(
            url, data, headers=self.authorization.authorization
        )
        try:
            with urllib.request.urlopen(req) as res:
                response = json.loads(res.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise HTTPError(e.reason, e.code)
        return response


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
        json_res = self.get_response(endpoint)
        result = Album(json_res)
        return result

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
        json_res = self.get_response(endpoint)
        result = Artist(json_res)
        return result

    def artists(self, artist_ids):
        """
        Get several artists information.
        Endpoint:GET https://api.spotify.com/v1/artists
        :param artist_ids: list of artist id. Maximum : 50 IDs
        :return: iterator of Artist objects
        """
        endpoint = 'https://api.spotify.com/v1/artists'
        # query validation
        if not isinstance(artist_ids, list):
            raise QueryValidationError('artist ids must be list.')
        if len(artist_ids) > 50:
            raise QueryValidationError('Too many ids. Maximum length is 50.')
        for each in artist_ids:
            if not isinstance(each, str):
                raise QueryValidationError('artist id must be str.')

        values = {
            'ids': ','.join(artist_ids)
        }

        data = urllib.parse.urlencode(values)
        full_url = endpoint + '?' + data
        json_res = self.get_response(full_url)
        converter = Artist.raw_to_object
        for result in json_res['artists']:
            yield converter(result)

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
        json_res = self.get_response(endpoint)
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
        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'.format(
            artist_id=artist_id
        )
        # coutry_code validation
        if not county_code:
            raise QueryValidationError('country_code is required parameter.')
        if not isinstance(county_code, str):
            raise QueryValidationError('country_code must be str.')

        values = {
            'country': county_code
        }
        data = urllib.parse.urlencode(values)
        full_url = endpoint + '?' + data
        json_res = self.get_response(full_url)
        converter = Track.raw_to_object
        for result in json_res['tracks']:
            yield converter(result)

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
        json_res = self.get_response(endpoint)
        result = Track(json_res)
        return result

    def audio_feature(self, track_id):
        """
        Get audio feature for track.
        :param track_id:
        :return: AudioFeature object
        """
        endpoint = 'https://api.spotify.com/v1/audio-features/{track_id}'.format(
            track_id=track_id
        )
        json_res = self.get_response(endpoint)
        result = AudioFeature(json_res)
        return result

    def paging(self, href):
        """
        paging for search result
        :param href: link to prev/next page
        :return: SearchResultDetail object or json format dict when raw is True.
        """
        if href:
            req = urllib.request.Request(
                href, headers=self.authorization.authorization
            )

            try:
                with urllib.request.urlopen(req) as res:
                    json_res = self.get_response(res)
            except urllib.error.HTTPError as e:
                raise HTTPError(e.reason, e.code)

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
            raise QueryValidationError('Query must be str.')
        if not q:
            raise QueryValidationError('Query is empty.')

        # convert tuple to list.
        if isinstance(search_type, tuple):
            search_type = list(search_type)
        # type validation
        if not isinstance(search_type, list):
            raise QueryValidationError('search_type must be list.')

        for t in search_type:
            try:
                if t.lower() not in SEARCH_TYPES:
                    raise QueryValidationError('{} is invalid search type.'.format(t))
            except AttributeError:
                raise AttributeError('Invalid type object in search_type. search_type must be list of string')

        # limit validation
        if not isinstance(limit, int):
            raise QueryValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        # offset validation
        if not isinstance(offset, int):
            raise QueryValidationError('offset must be int.')
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
        json_res = self.get_response(full_url)
        results = SearchResult(q, search_type, json_res)
        return results

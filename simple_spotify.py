import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from error import SpotifyHTTPError
from objects import Artist


class SpotifyBase:
    def __init__(self, client_id, client_secret):
        self.access_token = self.__auth__(client_id, client_secret)['access_token']

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


class Spotify(SpotifyBase):
    def __init__(self, client_id, client_secret):
        super().__init__(client_id, client_secret)
        self.header_params = {'Authorization': 'Bearer {}'.format(self.access_token)}

    def artists(self, artist_id, raw=False):
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
                json_res = json.loads(res.read().decode('utf-8'))
                if raw:
                    return json_res
                else:
                    return Artist(json_res)
        except urllib.error.HTTPError as e:
            raise SpotifyHTTPError(e.reason, e.code)

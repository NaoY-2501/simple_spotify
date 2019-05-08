import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime


ENDPOINT_TOKEN = 'https://accounts.spotify.com/api/token'


class SpotifyAuthBase:
    @classmethod
    def get_header_param(cls, client_id, client_secret):
        base64string = base64.encodebytes('{client_id}:{client_secret}'.format(
             client_id=client_id,
             client_secret=client_secret
        ).encode('utf-8'))

        authorization = 'Basic {base64string}'.format(
            base64string=base64string.decode('utf-8')
        ).replace('\n', '')  # trailing \n in base64string
        return {'Authorization': authorization}

    @classmethod
    def get_response(cls, headers, request_body):
        data = urllib.parse.urlencode(request_body).encode('ascii')
        req = urllib.request.Request(ENDPOINT_TOKEN, data, headers=headers)
        try:
            with urllib.request.urlopen(req) as res:
                res = json.loads(res.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise e
        return res


class ClientCredentialsFlow(SpotifyAuthBase):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.token_request()['access_token']
        self.token_type = self.token_request()['token_type']
        self.expires_in = self.token_request()['expires_in']

    @property
    def authorization(self):
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    def token_request(self):
        headers = self.get_header_param(self.client_id, self.client_secret)
        request_body = {'grant_type': 'client_credentials'}
        return self.get_response(headers, request_body)


class AuthorizationCodeFlow(SpotifyAuthBase):
    def __init__(self, client_id, client_secret, code, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.code = code
        self.created_at = datetime.now()
        self.redirect_uri = redirect_uri
        self.access_token = self.token_request()['access_token']
        self.token_type = self.token_request()['token_type']
        self.expires_in = self.token_request()['expires_in']
        self.scope = self.token_request()['scope']
        self.refresh_token = self.token_request()['refresh_token']

    @property
    def authorization(self):
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    def token_request(self):
        headers = self.get_header_param(self.client_id, self.client_secret)
        request_body = {
            'grant_type': 'authorization_code',
            'code': self.code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        return self.get_response(headers, request_body)

    def token_refresh(self):
        headers = self.get_header_param(self.client_id, self.client_secret)
        request_body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
        }
        self.access_token = self.get_response(headers, request_body)['access_token']
        self.created_at = datetime.now()

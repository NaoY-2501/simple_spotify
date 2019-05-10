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
    def __init__(self, access_token, token_type, expires_in, scope):
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.scope = scope

    @property
    def authorization(self):
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    @classmethod
    def token_request(cls, client_id, client_secret):
        headers = cls.get_header_param(client_id, client_secret)
        request_body = {'grant_type': 'client_credentials'}
        return cls.get_response(headers, request_body)


class AuthorizationCodeFlow(SpotifyAuthBase):
    def __init__(self, access_token, created_at, expires_in, scope, refresh_token, headers, token_type):
        self.access_token = access_token
        self.expires_in = expires_in
        self.scope = scope
        self.refresh_token = refresh_token
        self.created_at = created_at
        self.headers = headers
        self.token_type = token_type

    @property
    def authorization(self):
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    @classmethod
    def token_request(cls, client_id, client_secret, redirect_uri, code):
        headers = cls.get_header_param(client_id, client_secret)
        request_body = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
        }
        response = cls.get_response(headers, request_body)
        response['headers'] = headers
        response['created_at'] = datetime.now().strftime('%Y%m%d%H%M%S')
        return response

    def token_refresh(self):
        request_body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
        }
        self.access_token = self.get_response(self.headers, request_body)['access_token']
        self.created_at = datetime.now().strftime('%Y%m%d%H%M%S')

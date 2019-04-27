import base64
import hashlib
import json
import urllib.parse
import urllib.request
import webbrowser

from datetime import datetime

AUTH_ENDPOINT = 'https://accounts.spotify.com/authorize'
TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token'


def access_authorize_page(client_id, redirect_uri, scopes, state=None):
    data = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'show_dialog': True,
    }

    if state:
        data['state'] = hashlib.sha256(state.encode('utf-8')).hexdigest()

    params = urllib.parse.urlencode(data)

    url = f'{AUTH_ENDPOINT}?{params}'
    return url


def get_access_code():
    redirected_url = input('Enter the redirected URL :')
    code = urllib.parse.parse_qs(
        urllib.parse.urlsplit(redirected_url).query
    )['code'][0]
    return code


def make_authorization_header(client_id, client_secret):
    base64string = base64.encodebytes('{client_id}:{client_secret}'.format(
        client_id=client_id,
        client_secret=client_secret
    ).encode('utf-8'))

    headers = {'Authorization': 'Basic {base64string}'.format(
        base64string=base64string.decode('utf-8')
    ).replace('\n', '')}  # trailing \n in base64string
    return headers


def request_access_data(headers, redirect_uri, code):
    body = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }

    data = urllib.parse.urlencode(body).encode('ascii')
    req = urllib.request.Request(TOKEN_ENDPOINT, data, headers=headers)
    with urllib.request.urlopen(req) as res:
        jsonized_res = json.loads(res.read().decode('utf-8'))
    return jsonized_res


def main():
    print("""
    ======================================
                Simple-Spotify
        Authorization Code Flow Client
    ======================================
    """)

    client_id = input('Enter the your Client ID :')

    redirect_uri = input('Enter the redirect URI :')

    scopes = []
    cont = 'y'
    print('Enter the scopes')
    while cont == 'y':
        scope = input('Scope :')
        cont = input('Add more scope ?(y/n) :')
        scopes.append(scope)

    state = input('Enter the state (Optional, but strongly recommended) :')

    url = access_authorize_page(client_id, redirect_uri, scopes, state)
    webbrowser.open(url)

    code = get_access_code()

    client_secret = input('Enter the your Client Secret :')
    headers = make_authorization_header(client_id, client_secret)
    data = request_access_data(headers, redirect_uri, code)

    data['token'] = {
        'Bearer': data['access_token']
    }
    data['Authorization'] = headers['Authorization']
    now = datetime.now()
    data['created_at'] = now.strftime('%Y%m%d%H%M%S')
    data['redirect_uri'] = redirect_uri

    with open('simple-spotify_token.json', 'w') as fout:
        json.dump(data, fout, indent=4)


if __name__ == '__main__':
    main()

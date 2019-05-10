import hashlib
import json
import os
import urllib.parse
import urllib.request
import webbrowser

AUTH_ENDPOINT = 'https://accounts.spotify.com/authorize'


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


def main():
    print("""
    =============================================
                    Simple-Spotify
        Authorization Code Flow Support Tool
    =============================================

    Fetch authorization code from https://accounts.spotify.com/authorize.
    Output json file named simple-spotify_code.json.
    This json file includes client_id, client_secret, authorization code, redirect uri.
    Format of json file as follows.
    {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization code,
        'redirect_uri': redirect_uri
    }
    """)
    client_id = input('Enter the your Client ID :')

    client_secret = input('Enter the your Client Secret :')

    redirect_uri = input('Enter the redirect URI :')

    scopes = []
    cont = 'y'
    print('Enter the scopes')
    while cont == 'y':
        scope = input('Scope :')
        cont = input('Add more scope ?(y/n) :')
        scopes.append(scope)

    state = input('Enter the seed for generating CSRF token :')

    url = access_authorize_page(client_id, redirect_uri, scopes, state)
    webbrowser.open(url)

    code = get_access_code()

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri
    }

    current_dir = os.path.curdir
    fname = '{current_dir}/simple_spotify_code.json'.format(
        current_dir=current_dir
    )
    with open(fname, 'w') as fout:
        json.dump(data, fout, indent=4)


if __name__ == '__main__':
    main()

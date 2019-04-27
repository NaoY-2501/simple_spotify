import json
import pprint
import urllib.parse
import urllib.request
import webbrowser

ENDPOINT = 'https://accounts.spotify.com/authorize'


def input_params():
    client_id = input('Enter your Client ID :')

    redirect_uri = input('Enter redirect URI :')

    scopes = []
    cont = 'y'
    while cont == 'y':
        scope = input('Scope :')
        cont = input('Add more scope?(y/n) :')
        scopes.append(scope)

    state = input('Enter the state (Optional, but strongly recommended) :')

    data = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'show_dialog': True,
    }

    if state:
        data['state'] = state
    return data


def main():
    logo = """
    ======================================
    Simple-Spotify
    Authorization Code Get Client Tool
    ======================================
    """
    print(logo)

    data = input_params()

    params = urllib.parse.urlencode(data)

    url = f'{ENDPOINT}?{params}'

    webbrowser.open(url)

    redirected_url = input('Enter the redirected URL:')
    splited_url = urllib.parse.urlsplit(redirected_url)
    code = urllib.parse.parse_qs(splited_url.query)['code'][0]

    auth_params = {
        'client_id': data['client_id'],
        'redirect_uri': data['redirect_uri'],
        'code': code,
    }

    pprint.pprint(auth_params)
    print('Output authorization params...')
    with open('authorization_params.json', 'w') as f:
        json.dump(auth_params, f)
    print('Done !')


if __name__ == '__main__':
    main()

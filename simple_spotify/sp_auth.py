import urllib.parse
import urllib.request

ENDPOINT = 'https://accounts.spotify.com/authorize'


def main():
    logo = """
    ======================================
    Simple-Spotify
    Authorization Code Get Client Tool
    ======================================
    """
    print(logo)

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

    params = urllib.parse.urlencode(data)

    url = f'{ENDPOINT}?{params}'
    print(url)


if __name__ == '__main__':
    main()

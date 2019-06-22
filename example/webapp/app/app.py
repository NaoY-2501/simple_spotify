import hashlib
import urllib.parse
import os
import random
import string

from flask import Flask, request, session, redirect, render_template, url_for
from simple_spotify.api import Spotify
from simple_spotify.authorization import AuthorizationCodeFlow


AUTH_ENDPOINT = 'https://accounts.spotify.com/authorize'

CLIENT_ID = 'CLIENT_ID'

CLIENT_SECRET = 'CLIENT_SECRET'

SCOPES = [
    'user-read-email',
    'user-read-birthdate',
    'user-read-private',
    'user-top-read'
]

REDIRECT_URI = 'http://127.0.0.1:5000/callback/'

TERM = 'short_term'

TERM_DETAIL = {
    'short_term': 'Last 4 weeks',
    'medium_term': 'Last 6 months',
    'long_term': 'Last few years',
}

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.run(debug=True)


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


@app.route('/')
def top():
    if 'response' in session.keys():
        auth = AuthorizationCodeFlow(**session['response'])
        sp = Spotify(auth)
        user = sp.get_current_user_profile()
        top_artists = sp.get_users_top('artists', time_range=TERM)
        artists = top_artists.items
        top_tracks = sp.get_users_top('tracks', time_range=TERM)
        tracks = top_tracks.items

        return render_template('index.html', name=user.display_name, artists=artists, tracks=tracks, term=TERM_DETAIL[TERM])
    else:
        seed = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        url = access_authorize_page(CLIENT_ID, REDIRECT_URI, SCOPES, seed)
        return render_template('index.html', auth_url=url)


@app.route('/callback/')
def callback():
    """
    callback
    """
    session['response'] = AuthorizationCodeFlow.token_request(
        CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, request.args['code'])
    return redirect(url_for('top'))


@app.route('/logout')
def logout():
    """
    Logout
    """
    # Delete session data
    session.pop('response', None)
    return redirect('/')

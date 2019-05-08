# Simple-Spotify

Pure Python wrapper library for Spotify Web API.


## Installation

```
python setup.py install
```

## Quick Start

```python
from simple_spotify.api import Spotify
from simple_spotify.authorization import ClientCredentialsFlow

auth = ClientCredentialsFlow(
    'YOUR CLIENT ID',
    'YOUR CLIENT SECRET'
)

sp = Spotify(auth)

result = sp.search(q='sora tob sakana')

for album in result.albums.items:
    print(album.name)
```

```
sora tob sakana
cocoon ep
yozora wo zenbu
mahou no kotoba
```

If you execute endpoint which need AutotizationCodeFlow on your local envirnoment tempolary, 
`authcode-fetch` will be help you.

```
$ authcode-fetch

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

Enter the your Client ID : YOUR CLIENT ID
Enter the your Client Secret : YOUR CLIENT SECRET
Enter the redirect URI :http://127.0.0.1:8080/
Enter the scopes
Scope :user-read-birthdate
Add more scope ?(y/n) :n
# Open your default browser. Log in, authorize access
Enter the redirected URL : REDIRECTED URL
```

Then, simple-spotify_code.json generate on your current directory.

```python
import json

from simple_spotify.api import Spotify
from simple_spotify.authorization import AuthorizationCodeFlow

with open('simple-spotify_code.json') as f:
    auth_dict = json.load(f)

auth = AuthorizationCodeFlow(
    auth_dict['client_id'],
    auth_dict['client_secret'],
    auth_dict['code'],
    auth_dict['redirect_uri']
)

sp = Spotify(auth)

current_user = sp.get_current_user_profile()
```
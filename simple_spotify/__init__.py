from .api import Spotify
from .authcode_fetcher import main
from .authorization import ClientCredentialsFlow, AuthorizationCodeFlow
from .authcode_fetcher import main

__version__ = '1.0'


def authcode_fetch():
    main()

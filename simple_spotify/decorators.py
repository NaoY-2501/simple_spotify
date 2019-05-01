from datetime import datetime, timedelta

from .authorization import AuthorizationCodeFlow
from .errors import SpotifyIdsNotAssignedError


def has_ids(func):

    def wrapper(self, spotify_ids=None, **kwargs):
        if not spotify_ids:
            raise SpotifyIdsNotAssignedError
        result = func(self, spotify_ids, **kwargs)
        return result
    return wrapper


def token_refresh(func):

    def wrapper(self, *args, **kwargs):
        auth = self.authorization
        if isinstance(auth, AuthorizationCodeFlow):
            now = datetime.now()
            if auth.created_at + timedelta(seconds=auth.expires_in) < now:
                auth.token_refresh()
        result = func(self, *args, **kwargs)
        return result
    return wrapper

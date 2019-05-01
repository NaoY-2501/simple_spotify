from datetime import datetime, timedelta

from .authorization import AuthorizationCodeFlow
from .errors import SpotifyIdsNotAssignedError, QueryValidationError


def has_ids(func):

    def wrapper(self, spotify_ids=None, **kwargs):
        if not spotify_ids:
            raise SpotifyIdsNotAssignedError
        result = func(self, spotify_ids, **kwargs)
        return result
    return wrapper


def ids_validation(func):

    def wrapper(self, ids=None, **kwargs):
        # query validation
        if not isinstance(ids, list):
            raise QueryValidationError('IDs must be list.')
        if len(ids) > 50:
            raise QueryValidationError('Too many ids. Maximum length is 50.')
        for each in ids:
            if not isinstance(each, str):
                raise QueryValidationError('ID must be str.')
        return func(self, ids, **kwargs)
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

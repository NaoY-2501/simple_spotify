from datetime import datetime, timedelta

from .authorization import AuthorizationCodeFlow
from .errors import SpotifyIdsNotAssignedError, QueryValidationError, PathParameterError


def id_validation(func):
    def wrapper(self, path_param=None, **kwargs):
        if not path_param:
            raise SpotifyIdsNotAssignedError
        if not isinstance(path_param, str):
            raise PathParameterError('ID must be str')
        result = func(self, path_param, **kwargs)
        return result
    return wrapper


def ids_validation(func):
    def wrapper(self, ids=None, **kwargs):
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

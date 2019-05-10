import re

from datetime import datetime, timedelta

from .authorization import AuthorizationCodeFlow
from .consts import TUNEABLE_ATTRS
from .errors import PathParameterNotAssignedError, ValidationError, PathParameterError, RecommendationAttributeError

ATTR_PAT = re.compile(r'(?P<prefix>^(min|max|target)_)(?P<attr>[\w]+)')


def id_validation(param):
    def _validate(func):
        def wrapper(self, path_param=None, **kwargs):
            if not path_param:
                raise PathParameterNotAssignedError('{param} is required.'.format(
                    param=param
                ))
            if not isinstance(path_param, str):
                raise PathParameterError('{param} must be str'.format(
                    param=param
                ))
            result = func(self, path_param, **kwargs)
            return result
        return wrapper
    return _validate


def ids_validation(count):
    def _validate(func):
        def wrapper(self, ids=None, **kwargs):
            if not isinstance(ids, list):
                raise ValidationError('IDs must be list.')
            if len(ids) > count:
                raise ValidationError('Too many ids. Maximum length is .'.format(count))
            for each in ids:
                if not isinstance(each, str):
                    raise ValidationError('ID must be str.')
            return func(self, ids, **kwargs)
        return wrapper
    return _validate


def token_refresh(func):
    def wrapper(self, *args, **kwargs):
        auth = self.authorization
        if isinstance(auth, AuthorizationCodeFlow):
            now = datetime.now()
            created_at = datetime.strptime(auth.created_at, '%Y%m%d%H%M%S')
            if created_at + timedelta(seconds=auth.expires_in) < now:
                auth.token_refresh()
        return func(self, *args, **kwargs)
    return wrapper


def auth_validation(scopes):
    def _validate(func):
        def wrapper(self, *args, **kwargs):
            if not isinstance(self.authorization, AuthorizationCodeFlow):
                raise ValidationError('This endpoint is only for AuthorizationCodeFlow')
            for scope in scopes:
                if scope in self.authorization.scope.split(' '):
                    continue
                else:
                    raise ValidationError("Your authorization's scope does not have {scope}".format(
                        scope=','.join(scope)
                    ))
            return func(self, *args, **kwargs)
        return wrapper
    return _validate


def recommendations_validation(func):
    def wrapper(self, limit=20, market=None, seed_artists=None, seed_genres=None, seed_tracks=None, **kwargs):
        tuneable_attrs = locals()['kwargs'].keys()
        prefixes = ['min_', 'max_', 'target_']
        try:
            s = [ATTR_PAT.search(attr) for attr in tuneable_attrs]
            for attr in s:
                if attr.group('prefix') not in prefixes or attr.group('attr') not in TUNEABLE_ATTRS:
                    raise AttributeError
        except AttributeError:
            msg = 'Invalid Tuneable attribution: {attrs}'.format(
                attrs=','.join(list(tuneable_attrs))
            )
            raise RecommendationAttributeError(msg)
        return func(self, limit=limit, market=market, seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks, **kwargs)
    return wrapper

from datetime import datetime, timedelta

from .authorization import AuthorizationCodeFlow
from .errors import PathParameterNotAssignedError, ValidationError, PathParameterError


def id_validation(param='ID'):
    def _validate(func):
        def wrapper(self, path_param=None, **kwargs):
            if not path_param:
                raise PathParameterNotAssignedError
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
            if auth.created_at + timedelta(seconds=auth.expires_in) < now:
                auth.token_refresh()
        result = func(self, *args, **kwargs)
        return result
    return wrapper


def auth_validation(scope):
    def _validate(func):
        def wrapper(self, *args, **kwargs):
            if isinstance(self.authorization, AuthorizationCodeFlow):
                raise ValidationError('This endpoint is only for AuthorizationCodeFlow')
            if scope not in self.authorization.scope:
                raise ValidationError("Your authorization's scope does not have {scope}".format(
                    scope=scope
                ))
            return func(self, *args, **kwargs)
        return wrapper
    return _validate

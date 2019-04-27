from .errors import SpotifyIdsNotAssignedError


def has_ids(func):

    def wrapper(self, spotify_ids=None, **kwargs):
        if not spotify_ids:
            raise SpotifyIdsNotAssignedError
        result = func(self, spotify_ids, **kwargs)
        return result
    return wrapper

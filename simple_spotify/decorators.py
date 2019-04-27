from .errors import SpotifyIdsNotAssignedError


def has_ids(func):
    print(func)

    def wrapper(self, spotify_ids, *args, **kwargs):
        if not spotify_ids:
            raise SpotifyIdsNotAssignedError
        result = func(self, spotify_ids, *args, **kwargs)
        return result
    return wrapper

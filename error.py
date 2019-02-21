class SpotifyHTTPError(Exception):
    def __init__(self, reason, code):
        self.reason = reason
        self.status_code = code

    def __str__(self):
        return 'SpotifyHTTPError {status_code}:{reason}'.format(
            status_code=self.status_code,
            reason=self.reason
        )


class SpotifySearchTypeError(Exception):
    def __init__(self, invalid_type):
        self.reason = invalid_type

    def __str__(self):
        return 'SpotifySearchTypeError {reason} is invalid type.'.format(
            reason=self.reason
        )

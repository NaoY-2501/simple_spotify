class HTTPError(Exception):
    def __init__(self, reason, code):
        self.reason = reason
        self.status_code = code

    def __str__(self):
        return '{status_code}:{reason}'.format(
            status_code=self.status_code,
            reason=self.reason
        )


class QueryValidationError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class SpotifyIdsNotAssignedError(Exception):
    def __init__(self):
        self.reason = 'Spotify ID is not assigned.'

    def __str__(self):
        return self.reason


class PathParameterError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason

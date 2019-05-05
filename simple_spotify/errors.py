class HTTPError(Exception):
    def __init__(self, reason, code):
        self.reason = reason
        self.status_code = code

    def __str__(self):
        return '{status_code}:{reason}'.format(
            status_code=self.status_code,
            reason=self.reason
        )


class ExceptionBase(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class ValidationError(ExceptionBase):
    pass


class PathParameterNotAssignedError(ExceptionBase):
    pass


class PathParameterError(ExceptionBase):
    pass


class RecommendationAttributeError(ExceptionBase):
    pass

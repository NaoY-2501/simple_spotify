import json
import urllib.error
import urllib.request

from .errors import HTTPError


def get_response(authorization, url, data=None):
    req = urllib.request.Request(
        url, data, headers=authorization.authorization
    )
    try:
        with urllib.request.urlopen(req) as res:
            response = json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise HTTPError(e.reason, e.code)
    return response

import json
import urllib.error
import urllib.request

from .errors import HTTPError, ValidationError


def http_request(authorization, url, data=None, method='GET'):
    headers = authorization.authorization
    if method in ['POST', 'PUT', 'DELETE']:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(
        url, data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req) as res:
            if method == 'GET':
                response = json.loads(res.read().decode('utf-8'))
            else:
                response = res.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        raise HTTPError(e.reason, e.code)
    return response


def post_request(authorization, url, data=None):
    headers = authorization.authorization
    headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(
        url, data, headers=authorization.authorization, method='POST'
    )
    try:
        with urllib.request.urlopen(req) as res:
            response = json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise HTTPError(e.reason, e.code)
    return response


def validate_limit(limit, maximum=50):
    # validate limit
    if not isinstance(limit, int):
        raise ValidationError('limit must be int.')
    if limit > maximum:
        limit = maximum
    return limit


def validate_offset(offset, maximum=None):
    if not isinstance(offset, int):
        raise ValidationError('offset must be int.')
    if maximum and offset > maximum:
        offset = maximum
    return offset
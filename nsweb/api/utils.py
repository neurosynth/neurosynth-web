from flask import request


def make_cache_key():
    ''' Replace default cache key prefix with a string that also includes
    query arguments. '''
    return request.path + request.query_string.decode('utf-8')

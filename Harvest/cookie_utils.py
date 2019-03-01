from http import cookiejar


def cookie_to_dict(cookie):
    return {
        'name': cookie.name,
        'value': cookie.value,
        'domain': cookie.domain,
        'path': cookie.path,
        'expires': cookie.expires,
        'http_only': bool(cookie._rest.get('HttpOnly', False)),
        'secure': cookie.secure,
    }


def cookie_from_dict(data):
    return cookiejar.Cookie(
        name=data['name'],
        value=data['value'],
        domain=data['domain'],
        domain_initial_dot=data['domain'].startswith('.'),
        path=data['path'],
        expires=int(data['expires']),
        rest={'HttpOnly': data['http_only']},
        secure=data['secure'],

        version=0,
        domain_specified=True,
        port=None,
        port_specified=False,
        path_specified=data['path'] != '/',
        discard=False,
        comment=None,
        comment_url=None,
    )

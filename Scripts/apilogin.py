from warnings import warn
import requests


class WebApi(requests.Session):
    def __init__(self, name, user_agent, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                warn('{} overwrites default session attr'.format(key))
            setattr(self, key, value)

        self.name = name
        self.user_agent = user_agent
        self.headers = {'User-Agent': user_agent}

    def __repr__(self):
        return 'ApiRegister({})'.format(self.name)

    def authenticate(self, in_header=False):
        if in_header:
            header = {'app_id': self.app_id, 'app_key': self.app_key}
            self.headers.update(header)
        else:
            self.auth = (self.app_id, self.app_key)


class TokenWebApi(WebApi):
    def __init__(self, name, user_agent, token_url, token_data, **kwargs):
        super().__init__(name, user_agent, **kwargs)
        self.token_url = token_url
        self.token_data = token_data

        # monkey patched Session's request method
        self.request = self.refresh_token(self.request)

    def get_access_token(self, token_url=None, token_data=None):
        if not token_url:
            token_url = self.token_url

        if not token_data:
            token_data = self.token_data

        response = self.request('post', token_url, token_data)
        token_resp = response.json()
        str_fmt = (token_resp['token_type'], token_resp['access_token'])
        access_token_header = {'Authorization': '{} {}'.format(*str_fmt)}
        self.headers.update(access_token_header)
        self.auth = ()

    def refresh_token(self, request_function):
        def wrapper(*args, **kwargs):
            response = request_function(*args, **kwargs)
            if response.status_code == 403:
                self.authenticate()
                self.get_access_token()
                response = request_function(*args, **kwargs)
            return response
        return wrapper


if __name__ == '__main__':
    import tools

    # no auth
    name = 'UrbanDictionary'
    user_agent = 'Botreplier by UrbanDict_Bot'
    urbandict_api_url = 'http://api.urbandictionary.com/v0/define?term=hettie'

    apireg = WebApi(name, user_agent)
    response = apireg.request(method='get', url=urbandict_api_url)
    print('no auth:', response.status_code)

    # key auth
    name = 'dictionary'
    key_header = tools.get_creds('..\\private\\dict_creds.txt')
    dictapi = WebApi(name, user_agent, **key_header)
    dictapi.authenticate(in_header=True)
    dictionary_url = 'https://od-api.oxforddictionaries.com/api/v2/entries/en-us/cromulent'
    response2 = dictapi.request(method='get', url=dictionary_url)
    print('key auth:', response2.status_code)

    # redditapi oauth
    name = 'Reddit'
    token_url = 'https://www.reddit.com/api/v1/access_token'
    call_url = 'https://oauth.reddit.com/api/v1/me'
    useragent = 'Replybot by UrbanDict-bot (v1.0)'
    logins = tools.get_creds('..\\private\\reddit_creds.txt')
    token_data = {'grant_type': 'password',
                  'password': logins['password'],
                  'username': logins['username']}

    reddapi = TokenWebApi(name, useragent, token_url, token_data, **logins)
    response3 = reddapi.request('get', call_url)
    print('oauth:', response3.status_code)

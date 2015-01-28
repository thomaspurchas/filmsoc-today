import requests


class Movie:
    pass


class TraktClient:

    def __init__(self, client_id):
        self.API_ENDPOINT = "https://api.trakt.tv/"
        self.client_id = client_id
        self.oAuth = False

    def set_oAuth_token(self, token):
        self.oAuth_token = token
        self.oAuth = True

    def _make_req(self, endpoint, **query_params):
        headers = {
            'trakt-api-version': '2',
            'trakt-api-key': self.client_id,
            'Content-Type': 'application/json'
        }

        uri = '%s%s' % (self.API_ENDPOINT, endpoint)

        if self.oAuth:
            headers['Authorization'] = 'Bearer %s' % self.oAuth_token

        r = requests.get(uri, headers=headers, params=query_params)

        return r.json()

    def movies(self, id, extended=None):
        ENDPOINT = "movies/"

        uri = '%s%s' % (ENDPOINT, id)

        return self._make_req(uri, extended=extended)

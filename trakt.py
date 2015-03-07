import requests


class TraktAPIError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Releases(list):

    def __getitem__(self, key):
        filtered = filter(lambda c: str(c['country']) == key, self)
        if len(filtered) == 1:
            return filtered[0]
        else:
            raise KeyError


class Movie(object):

    def __init__(self, id, trakt_client=None):

        self.id = id
        self._cache = None
        self._trakt_client = trakt_client
        self._sparse = False

    @classmethod
    def create_sparse(cls, json, trakt_client=None):
        obj = cls(json['ids']['trakt'], trakt_client)
        obj._sparse = True
        obj._cache = json

        return obj

    def __getitem__(self, key):

        if self._cache is None and self._trakt_client and not self._sparse:
            self._cache = self._trakt_client._movies(self.id, 'full,images')
            self.id = self._cache['ids']['trakt']

        if key == 'releases':
            if self._cache.get('releases', None) is None:
                releases = self._trakt_client._releases(self.id)

                self._cache['releases'] = Releases(releases)

        if key == 'ratings':
            if self._cache.get('ratings', None) is None:
                ratings = self._trakt_client._ratings(self.id)

                self._cache['ratings'] = ratings

        try:
            result = self._cache[key]
        except KeyError as e:
            if self._sparse:
                self._sparse = False
                self._cache = self._trakt_client._movies(self.id, 'full,images')._cache

                result = self._cache[key]
            else:
                raise e

        return result


class TraktClient(object):

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
        if r.status_code != requests.codes.ok:
            raise TraktAPIError('HTTP %s status code returned' % r.status_code)

        return r.json()

    def _movies(self, id, extended=None):
        ENDPOINT = "movies/"

        uri = '%s%s' % (ENDPOINT, id)

        json = self._make_req(uri, extended=extended)

        return json

    def _releases(self, id):
        ENDPOINT = "movies/%s/releases/"

        uri = ENDPOINT % id

        return self._make_req(uri)

    def _ratings(self, id):
        ENDPOINT = "movies/%s/ratings/"

        uri = ENDPOINT % id

        return self._make_req(uri)

    def movies(self, id):
        return Movie(id, self)

    def search(self, query, query_type=None):
        ENDPOINT = "search"

        uri = ENDPOINT

        json = self._make_req(uri, query=query, type=query_type)

        results = []
        for item in json:
            if item['type'] == 'movie':
                item['movie'] = Movie.create_sparse(item['movie'], self)
                results.append(item)
            else:
                results.append(item)

        return results


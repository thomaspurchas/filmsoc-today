import tmdbsimple

tmdbsimple.API_KEY = 'b25954e24d335eccb515c9b742882534'
tmdb_configuration = tmdbsimple.Configuration()
tmdb_configuration.info()
tmdb_secure_base_url = tmdb_configuration.images['secure_base_url']


class TMDB(object):

    def __init__(self):
        self.configuration = tmdbsimple.Configuration()
        self.secure_base_url = self.configuration.images['secure_base_url']

    def get_film(self, filmsoc_film):

        if filmsoc_film.imdb_id:
            tmdb_result = tmdbsimple.Find(
                filmsoc_film.imdb_id).info(external_source='imdb_id')
            tmdb_film = tmdbsimple.Movies(
                tmdb_result['movie_results'][0]['id'])
            tmdb_film.info()
            tmdb_images = tmdb_film.images()
            tmdb_backdrops = sorted(
                tmdb_images['backdrops'], key=lambda image: image['vote_average'], reverse=True)
            tmdb_posters = sorted(
                tmdb_images['posters'], key=lambda image: image['vote_average'], reverse=True)
            return '<img src=%s><img src=%s>' % (urljoin(tmdb_secure_base_url, 'original' + tmdb_backdrops[0]['file_path']), urljoin(tmdb_secure_base_url, 'w780' + tmdb_posters[0]['file_path']))

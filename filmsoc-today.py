from flask import Flask
from werkzeug.contrib.cache import SimpleCache
from urlparse import urljoin
from filmsoc import filmsoc


IMDB_ID_REGEX = "([0-9]{7})"

app = Flask(__name__)
app.debug = True
cache = SimpleCache()




def get_films():
    cached = cache.get('films')
    if not cached:
        cached = filmsoc.films_coming_soon()
        cache.set('films', cached, 5 * 60)

    return cached


def get_todays_film():
    films = get_films()

    films.sort(key=lambda film: film.show_times[0], reverse=True)

    if len(films) > 0:
        return films[0]
    else:
        return None


@app.route('/')
def today():
    film = get_todays_film()
    if not film:
        return ''



if __name__ == '__main__':
    app.run()

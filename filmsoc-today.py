import os
import errno
from flask import Flask, send_file, render_template, url_for
from werkzeug.contrib.cache import SimpleCache
from urlparse import urljoin
import requests
import humanize
from filmsoc import filmsoc
from trakt import TraktClient

IMDB_ID_REGEX = "([0-9]{7})"

app = Flask(__name__)
app.debug = True
cache = SimpleCache()

TRAKT_CLIENT_ID = 'f64b34c319adf822739628b20097fa13ce9da1011bcf29a08f5f96be277825b4'
TRAKT_OAUTH_TOKEN = 'bfc7781db2e5ac5633e98c1339e042d78d80a3c718f6e0f68b3a4b44d2902349'

TRAKT_CLIENT = TraktClient(TRAKT_CLIENT_ID)
TRAKT_CLIENT.set_oAuth_token(TRAKT_OAUTH_TOKEN)

APP_LOCATION = os.path.dirname(os.path.realpath(__file__))
TEMP_IMAGE_LOC = os.path.join(APP_LOCATION, 'images/')


def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def get_films():
    cached = cache.get('films')
    if not cached:
        cached = filmsoc.films_coming_soon()
        cache.set('films', cached, 5 * 60)

    return cached


def get_todays_film():
    films = get_films()

    films.sort(key=lambda film: film.show_times[0])

    if len(films) > 0:
        return films[0]
    else:
        return None


def download_file(url, local_filename):
    r = requests.get(url, stream=True)
    mkdir_p(os.path.dirname(local_filename ))
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename


def get_trakt_image(imdb_id, image_type):
    image_path = 'trakt/%s/%s.jpg' % (imdb_id, image_type)
    image_path = os.path.join(TEMP_IMAGE_LOC, image_path)

    if image_type not in ['fanart', 'poster', 'logo', 'clearart', 'banner', 'thumb']:
        return 'Sorry Pal', 403

    if not os.path.exists(image_path):
        m = TRAKT_CLIENT.movies(imdb_id)
        print imdb_id
        print 'Getting trakt image url'
        url = m['images'][image_type]['full']

        print 'downloading', url
        download_file(url, image_path)

    return send_file(image_path)


@app.context_processor
def image_processor():
    def get_movie_image(service, image_type):
        movie_id = get_todays_film().id
        return url_for('get_image', movie_id=movie_id, service=service, image_type=image_type)
    return dict(get_movie_image=get_movie_image)


@app.route('/image/<movie_id>/<service>/<image_type>')
def get_image(movie_id, service, image_type):
    todays_film = get_todays_film()
    imdb_id = filmsoc.get_imdb(movie_id)
    print todays_film.id
    # if movie_id != todays_film.id:
    #     return 'Sorry Pal', 403

    if service == 'trakt':
        return get_trakt_image(imdb_id, image_type)
    else:
        return 'You sure?', 401


@app.route('/')
def today():
    film = get_todays_film()
    if not film:
        return ''

    date = humanize.naturalday(film.show_times[0]).title()

    return render_template('home.html', film_id=film.id, film_title=film.title, date=date)



if __name__ == '__main__':
    app.run()

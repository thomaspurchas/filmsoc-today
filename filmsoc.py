from datetime import datetime
import re
import requests

IMDB_ID_REGEX = "([0-9]{7})"

COMINGSOON_URL = 'https://www.filmsoc.warwick.ac.uk/automatic/comingsoon/json'
COMINGSOON_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Film(object):

    def __init__(self, film_data):
        self.title = film_data['title']
        self.id = film_data['film_id']
        self.review = film_data['review']
        self.gauge = film_data['gauge'].lower()

        if film_data['runtime'].strip() != '':
            self.runtime = int(film_data['runtime'])
        else:
            self.runtime = None

        if film_data['year'].strip() != '':
            self.year = datetime.strptime(film_data['year'], '%Y').date()
        else:
            self.year = None

        self.show_times = []
        show_times = film_data['dates'].split(',')
        for show_time in show_times:
            self.show_times.append(
                datetime.strptime(show_time, COMINGSOON_DATETIME_FORMAT))
        self.show_times.sort()

        match = re.search(IMDB_ID_REGEX, film_data['imdb_url'])
        if match:
            self.imdb_id = 'tt' + match.group(0)
        else:
            self.imdb_id = None


class Filmsoc(object):

    def films_coming_soon(self):
        r = requests.get(COMINGSOON_URL)

        films = []
        for film in r.json():
            films.append(Film(film))

        return films

filmsoc = Filmsoc()

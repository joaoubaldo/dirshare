from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.config import Configurator
from pymongo.mongo_client import MongoClient

def get_mongo_db(request):
    s = request.registry.settings
    c = MongoClient(s.get('mongo.host'), int(s.get('mongo.port')))
    c[s.get('mongo.db')].thumbnails.ensure_index( [('path', 1)] )

    return c[s.get('mongo.db')]


@subscriber(NewRequest)
def add_mongo_db(event):
    event.request.set_property(get_mongo_db, 'db', reify=True)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('view_image', '/i/{size}')
    config.add_route('stream_image', '/stream/{size}')
    config.add_route('zip_page', '/zpage')

    config.scan()
    return config.make_wsgi_app()

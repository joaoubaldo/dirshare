""" This module implements the whole dirshare wsgi application """

from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.config import Configurator
from pymongo.mongo_client import MongoClient


def get_mongo_db(request):
    """
    Reads app settings and returns a mongo Database instance.

    @param is the Request object
    @returns mongodb Database instance
    """
    s = request.registry.settings
    c = MongoClient(s.get('mongo_host'), int(s.get('mongo_port')))
    c[s.get('mongo_db')].thumbnails.ensure_index( [('path', 1)] )
    return c[s.get('mongo_db')]


@subscriber(NewRequest)
def add_mongo_db(event):
    """
    Event handler
    """
    event.request.set_property(get_mongo_db, 'db', reify=True)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_mako')

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('view_image', '/i/{size}')
    config.add_route('stream_image', '/stream/{size}')
    config.add_route('zip_page', '/zpage')

    config.scan()
    return config.make_wsgi_app()

""" This module implements the whole dirshare wsgi application """

from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.config import Configurator

from dirshare.data_access import data_access_factory

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("dirshare")

def get_db(request):
    """
    Reads app settings and returns a IDirshareDataAccess instance.

    @param is the Request object
    @returns IDirshareDataAccess instance
    """

    s = request.registry.settings
    db = data_access_factory(s.get('db_uri'))
    db.setup()

    return db


@subscriber(NewRequest)
def add_db(event):
    """
    Event handler
    """
    event.request.set_property(get_db, 'db', reify=True)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_mako')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('stream_image', '/stream/{size}')
    config.add_route('zip', '/zip')

    config.add_route('ajax_home', '/')
    config.add_route('ajax_listdir', '/app/listdir')
    config.add_route('ajax_meta', '/app/meta')
    config.add_route('ajax_setup', '/app/setup')
    config.add_route('ajax_rebuild', '/app/rebuild')
    config.add_route('ajax_getjobs', '/app/getjobs')


    config.scan()
    return config.make_wsgi_app()

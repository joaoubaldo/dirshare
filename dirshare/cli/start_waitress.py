#!/usr/bin/python
#

""" 
This module implements the CLI application, used to launch a server and
serve dirshare wsgi application using waitress server.
"""

import os
import sys
import logging
from optparse import OptionParser
try:
    # for python 2
    from urlparse import urlparse
except ImportError:
    # for python 3
    from urllib.parse import urlparse

from waitress import serve

from dirshare import main as m
from dirshare import VERSION

cfg = {
    'pyramid.reload_templates': True,
    'pyramid.debug_authorization': False,
    'pyramid.debug_notfound': False,
    'pyramid.debug_routematch': False,
    'pyramid.default_locale_name': "en",
    'mako.directories': "dirshare:templates",
    'db_uri': "mongodb://localhost:27017/dirshare",
    'images_per_page': 10,
    'image_sizes': "128x128 600x600 1000x1000 full",
    'images_root': ".",
    'resize_format': "PNG",
    'resize_quality': 90,
}

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("dirshare")

def main():
    log.info("Starting dirshare %s..." % (VERSION,))
    """
    Entry point
    """
    parser = OptionParser()

    parser.add_option("-r", "--images-root", 
        dest="images_root", action="store", default="%(images_root)s" % cfg,
        help="Root directory to share (default: \"%(images_root)s\")" % cfg)

    parser.add_option("-s", "--image-sizes",
        dest="image_sizes", action="store", default="%(image_sizes)s" % cfg,
        help="Available sizes as a string (default: \"%(image_sizes)s\")" % cfg)

    parser.add_option("-f", "--resize-format",
        dest="resize_format", action="store", default="%(resize_format)s" % cfg,
        help="Resize encoder to user (default: \"%(resize_format)s\")" % cfg)

    parser.add_option("-q", "--resize-quality",
        dest="resize_quality", action="store", default="%(resize_quality)d" % cfg,
        help="Resize quality value to pass to encoder (default: %(resize_quality)d)" % cfg)

    parser.add_option("-d", "--db-uri",
        dest="db_uri", action="store",
        default="%(db_uri)s" % cfg,
        help="DB uri (default: \"%(db_uri)s\")" % cfg)

    parser.add_option("-p", "--http-port",
        dest="http_port", action="store", default=6543,
        help="HTTP listen port (default: %d)" % (6543,))

    parser.add_option("-b", "--http-ip",
        dest="http_ip", action="store", default="127.0.0.1",
        help="HTTP bind ip (default: \"%s\")" % ("127.0.0.1",))

    (options, args) = parser.parse_args()

    ''' Override defaults when needed '''
    for k in cfg.keys():
        if hasattr(options, k) and getattr(options, k) is not None:
            cfg[k] = getattr(options, k)

    ''' Parse db uri '''
    db = urlparse(options.db_uri)
    if db.scheme not in ['mongodb']:
        raise ValueError("DB scheme not supported")
    cfg['mongo_host'] = db.hostname
    cfg['mongo_port'] = db.port
    cfg['mongo_db'] = db.path[1:]

    ''' Boot log '''
    log.info("Config options:")
    for o in parser.option_list:
        if o.action == 'store':
            log.info("config.%s = %s" % (o.dest, getattr(options, o.dest) or o.default) )

    from PIL import _imaging
    log.info("Available pillow decoders: %s" % (', '.join( [k[:-8] for k in dir(_imaging) if k.endswith("_decoder")] ),))

    ''' Serve the app '''
    wsgiapp = m({}, **cfg)
    log.info("App created, serving...")
    serve(wsgiapp,
          host=options.http_ip,
          port=options.http_port)

if __name__ == "__main__" :
    main()

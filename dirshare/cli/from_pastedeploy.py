#!/usr/bin/python
#

""" 
This module implements the CLI application, used to launch a server and
serve dirshare wsgi application given a pastedeploy ini file.
"""

import os
import sys
from optparse import OptionParser

from paste.deploy import loadapp
from paste.deploy import loadserver


ini_template = '''
###
# app configuration
# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/environment.html
###

[app:main]
use = egg:dirshare

pyramid.reload_templates = false
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.default_locale_name = en

mako.directories = dirshare:templates

#db_uri = sqlite://:memory:
db_uri = mongodb://localhost:27017/dirshare

images_per_page = 10
image_sizes = 128x128 600x600 1000x1000 full
images_root = ~/
resize_format = JPEG
resize_quality = 90

###
# wsgi server configuration
###

[server:main]
use = egg:waitress#main
host = 127.0.0.1
port = 6543

###
# logging configuration
# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/logging.html
###

[loggers]
keys = root, dirshare

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console

[logger_dirshare]
level = DEBUG
handlers =
qualname = dirshare

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s
'''

def main():
    """
    Entry point
    """
    parser = OptionParser()

    parser.add_option("-c", "--config", 
        dest="config", action="store",
        help="Server configuration file path")

    parser.add_option("-r", "--images-root", 
        dest="images_root", action="store",
        help="Root directory to share (will override config file)")

    parser.add_option("-e", "--example-ini",
        dest="example_ini", action="store",
        help="Create an example ini file")

    (options, args) = parser.parse_args()

    if options.example_ini:
        f = open(options.example_ini, 'w')
        f.write(ini_template)
        f.close()
        return

    if not options.config:
        parser.error("No config file specified")

    ini = 'config:%s' % (options.config,)
    app = loadapp(ini, relative_to='.')
    server = loadserver(ini, relative_to='.')

    if options.images_root:
        app.registry.settings['images_root'] = options.images_root

    server(app)

if __name__ == "__main__" :
    main()

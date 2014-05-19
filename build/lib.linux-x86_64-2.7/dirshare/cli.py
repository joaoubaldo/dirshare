#!/usr/bin/python
#

""" 
This module implements the CLI application, used to launch a server and 
serve the dirshare wsgi application 
"""

import os
import sys
from optparse import OptionParser

from paste.deploy import loadapp
from paste.deploy import loadserver


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

    (options, args) = parser.parse_args()

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

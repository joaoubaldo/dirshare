#!/usr/bin/python
#

import os
import sys
from optparse import OptionParser

from paste.deploy import loadapp
from paste.deploy import loadserver

def main():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config", action="store",
                      help="Server configuration file path")
    parser.add_option("-d", "--directory", dest="directory", action="store",
                      help="Shared directory path (will override config file)")
    (options, args) = parser.parse_args()

    if not options.config:
        parser.error("No config file specified")


    ini = 'config:%s' % (options.config,)
    app = loadapp(ini, relative_to='.')
    server = loadserver(ini, relative_to='.')

    if options.directory:
        app.registry.settings['images_root'] = options.directory

    server(app)

if __name__ == "__main__" :
    main()

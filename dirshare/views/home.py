import os
import math
import mimetypes
from base64 import b64encode, b64decode

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from paste.deploy.converters import aslist, asint
from pyramid.view import view_config

from dirshare.utils import *


"""
Home page
"""
@view_config(route_name='home', renderer='dirshare:templates/home.mako')
def view_home(request):
    sizes = aslist(request.registry.settings.get('image_sizes'))
    root = request.registry.settings.get('images_root')
    path = request.params.get('d', '')
    full_path = "%s/%s" % (root, path)
    page = int(request.params.get('p', 0))
    per_page = int(request.params.get('pp', 
        request.registry.settings.get('images_per_page')))

    if '..' in path: 
        return HTTPForbidden()

    try:
        contents = get_dir_contents(full_path)
    except OSError:
        return HTTPNotFound()

    return {
        'nav_path': build_path_breadcrumb(path),  # navigation path list
        'image_count': len([c for c in contents if c[0] == False]),
        'thumbnail_size': sizes[0],
        'sizes': sizes,
        'page': page,
        'per_page': per_page,
        'pages': range(int(math.ceil(len(contents)/per_page)) + 1),
        'contents': contents[page*per_page:page*per_page+per_page], 
        'path': path }

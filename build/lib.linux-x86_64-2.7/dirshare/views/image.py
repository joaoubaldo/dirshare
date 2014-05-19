import os

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from paste.deploy.converters import aslist, asint
from pyramid.view import view_config

from dirshare.utils import *


@view_config(route_name='view_image', 
    renderer='dirshare:templates/view_image.mako')
def view_image(request):
    """
    View single image page
    """
    sizes = aslist(request.registry.settings.get('image_sizes'))
    size = request.matchdict['size']
    root = request.registry.settings.get('images_root')
    path = request.params.get('d', '')
    full_path = "%s/%s" % (root, path)
    dir_ = os.path.dirname(path)
    page = int(request.params.get('p', 0))
    per_page = int(request.params.get('pp', 
        request.registry.settings.get('images_per_page')))

    if '..' in path: 
        return HTTPForbidden()

    contents = get_dir_contents("%s/%s" % (root, dir_), sorted_=True, only='f')

    mid_idx = None
    for idx, (is_dir, c) in enumerate(contents):
        if c == os.path.basename(path):
            mid_idx = idx
            break

    prev, next = None, None
    if mid_idx is not None:
        try:
            if mid_idx >= 1:
                prev = contents[mid_idx-1]
        except IndexError:
            prev = None
        try:
            next = contents[mid_idx+1]
        except IndexError:
            next = None

        contents = contents[mid_idx-int(per_page/2):mid_idx] + \
            contents[mid_idx+1:mid_idx+int(per_page/2)]
    else:
        contents = []


    return {
        'nav_path': build_path_breadcrumb(os.path.dirname(path)),
        'thumbnail_size': sizes[0],
        'siblings': contents,
        'prev_sibling': prev,
        'next_sibling': next,
        'path': path,
        'dir': dir_,
        'size': size,
        'sizes': sizes
    }

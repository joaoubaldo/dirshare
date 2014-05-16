from StringIO import StringIO
from zipfile import ZipFile
import os
import mimetypes

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from pyramid.response import Response
from pyramid.view import view_config

from dirshare.utils import *


@view_config(route_name='zip_page')
def view_zip_page(request):
    root = request.registry.settings.get('images_root')
    path = request.params.get('d', '')
    full_path = "%s/%s" % (root, path)
    page = int(request.params.get('p', 0))
    per_page = int(request.params.get('pp',  
        request.registry.settings.get('images_per_page')))

    if '..' in path:
        return HTTPForbidden()

    contents = get_dir_contents(full_path)

    """
    Zip files
    """
    zdata = StringIO()
    zip_ = ZipFile(zdata, 'w')
    for is_dir, c in contents[page*per_page:page*per_page+per_page]:
        if not is_dir:
            f = "%s/%s" % (full_path, c)
            zip_.write(f)
    zip_.close()

    data = zdata.getvalue()
    zip_type = mimetypes.guess_type('dummy.zip')[0]
    headers = [('Content-Type', str(zip_type)),
           ('Cache-Control', 'no-cache'),
           ('Content-Length', str(len(data))) ]

    return Response(body=data, headerlist=headers)

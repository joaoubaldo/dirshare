import os
import mimetypes
from base64 import b64encode, b64decode
from datetime import datetime

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from paste.deploy.converters import aslist, asint
from pyramid.response import Response
from pyramid.view import view_config
from PIL import Image

from dirshare.utils import *


"""
Stream image request
"""
@view_config(route_name='stream_image')
def view_stream_image(request):
    sizes = aslist(request.registry.settings.get('image_sizes'))
    root = request.registry.settings.get('images_root')
    format_ = request.registry.settings.get('resize_format')
    quality = asint(request.registry.settings.get('resize_quality'))
    size = request.matchdict['size']
    path = request.params.get('d', '')
    full_path = "%s/%s" % (root, path)

    if not path or '..' in path:
        return HTTPForbidden()

    if size not in sizes:
        return HTTPNotFound('size not allowed')

    if size == 'full':
        data, headers = stream_image(
            full_path, 
            scale=None)
    elif size == sizes[0]:  # Thumbnail?
        thumb_doc = request.db.thumbnails.find_one({"path": path})

        if thumb_doc is None:
            f = Image.open(full_path, 'r')
            f.thumbnail((128,128), Image.NEAREST)
            data_ = StringIO()
            f.save(fp=data_, format="JPEG", quality=35)
            data = data_.getvalue()
            headers = [('Content-Type', mimetypes.guess_type(full_path)[0]),
                   ('Cache-Control', 'no-cache'),
                   ('Content-Length', str(len(data))) ]
            thumb_doc = {
                'path': full_path,
                'mime_type': mimetypes.guess_type(full_path)[0],
                'insert_date': datetime.now(),
                'content': b64encode(data)
            }
            request.db.thumbnails.insert(thumb_doc)
        else:
            data = b64decode(thumb_doc['content'])
            headers = [('Content-Type', str(thumb_doc['mime_type'])),
                   ('Cache-Control', 'no-cache'),
                   ('Content-Length', str(len(data))) ]
    else:
        data, headers = stream_image(
            full_path, 
            scale=sizestring_to_tuple(size), 
            format_=format_,
            quality=quality)

    return Response(body=data, headerlist=headers)

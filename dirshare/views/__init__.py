import os
import math
import mimetypes
import json
from base64 import b64encode, b64decode
from datetime import datetime
from StringIO import StringIO
from zipfile import ZipFile

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden, HTTPNotModified
from paste.deploy.converters import aslist, asint
from pyramid.response import Response
from pyramid.view import view_config
from PIL import Image
import exifread

from dirshare import utils


@view_config(route_name='ajax_home', renderer='dirshare:templates/ajax_home.mako')
def view_ajax_home(request):
    """
    Render the single html template.
    """
    return {}


@view_config(route_name='ajax_listdir', renderer='json')
def view_ajax_listdir(request):
    """
    This view returns a json object representing a specific path, including number of pages, files, directories.
    Input request parameters: path, per_page, page.
    """
    sizes = aslist(request.registry.settings.get('image_sizes'))
    root = request.registry.settings.get('images_root')
    per_page = int(request.params.get('pp', 
        request.registry.settings.get('images_per_page')))
    path = request.params.get('d', '')
    page = int(request.params.get('p', 0))
    full_path = "/".join([root, path])

    if '..' in path: 
        return HTTPForbidden()

    directories = []
    files = []
    remaining = per_page
    for c in os.listdir(full_path):
        f = "%s/%s" % (full_path, c)
        mt = mimetypes.guess_type(f)
        if os.path.isfile(f) and mt[0] and mt[0].startswith('image'):
            files.append({'name': c})
        elif os.path.isdir(f):
            directories.append({'name': c})
    files = sorted(files, key=lambda i: i['name'])
    directories = sorted(directories, key=lambda i: i['name'])

    return {
        'nav_path': utils.fs.build_path_breadcrumb(path),  # navigation path list
        'image_count': len(files),
        'thumbnail_size': sizes[0],
        'sizes': sizes,
        'page': page,
        'per_page': per_page,
        'pages': range(int(math.ceil(len(files)/float(per_page)))),
        'files': files[page*per_page:page*per_page+per_page],
        'directories': directories,
        'path': path
        }


@view_config(route_name='ajax_meta', renderer='json')
def view_ajax_meta(request):
    """
    This view returns a json object with metadata for a specific file.
    Input request parameters: path
    """
    root = request.registry.settings.get('images_root')
    path = request.params.get('d', '')
    full_path = "/".join([root, path])

    if '..' in path: 
        return HTTPForbidden()

    meta = utils.db.get_meta_from_db(request.db, full_path)

    return {
        'path': path,
        'exif': meta['exif'] if meta else {}
        }

@view_config(route_name='ajax_setup', renderer='json')
def view_ajax_setup(request):
    """
    This view returns a json object with essential parameters to configure the application.
    """
    meta_url = request.route_url('ajax_meta', 
        _query={'d': "__PATH__"})
    stream_url = request.route_url('stream_image', 
        size="__SIZE__",
        _query={'d': "__PATH__"})
    listdir_url = request.route_url('ajax_listdir', 
        _query={'d': '__PATH__', 'pp': '__PERPAGE__', 'p': '__PAGE__'})
    zip_url = request.route_url('zip', 
        _query={'files': "__FILES__"})
    
    return {
        'meta_url': meta_url,
        'stream_url': stream_url,
        'listdir_url': listdir_url,
        'zip_url': zip_url,
        'sizes': aslist(request.registry.settings.get('image_sizes')),
        'thumb_size': aslist(request.registry.settings.get('image_sizes'))[0]
        }
        
        
@view_config(route_name='stream_image')
def view_stream_image(request):
    """
    Stream image.
    Receives a specific image path name and returns the image content.
    Thumbnail caching is done in here.
    """
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
        f = open(full_path, 'r')
        data = f.read()
        mime = utils.image.get_mimetype(full_path)
    else:
        doc = utils.db.get_resize_from_db(request.db, full_path, size)
        if not doc:
            data = utils.image.resize(full_path, size, format_, quality)
            doc = utils.db.save_resize_to_db(request.db, full_path, size, 
                data)
            utils.db.save_meta_to_db(request.db, full_path, force=True)

        data = b64decode(doc['content'])
        mime = doc['mime_type']
        
    headers = [
        ('Content-Type', str(mime)),
        ('Content-Length', str(len(data))),
        ('Content-Disposition', str("attachment; filename=\"%s\"" % 
            (os.path.basename(full_path),)))
        ]

    resp = Response(body=data, headerlist=headers)
    resp.md5_etag(data)
    if hasattr(request, 'if_none_match') and \
    resp.etag in request.if_none_match:
        raise HTTPNotModified()

    return resp


@view_config(route_name='zip')
def view_zip(request):
    """ 
    Zip view.
    Receives a list of files to export and returns a zip file with them.
    """
    root = request.registry.settings.get('images_root')
    files = json.loads(request.params.get('files', ''))
    
    for f in files:
        if '..' in f:
            return HTTPForbidden()

    """
    Zip files
    """
    zdata = StringIO()
    zip_ = ZipFile(zdata, 'w')
    for f in files:
        f = "%s/%s" % (root, f)
        if os.path.isfile(f):
            zip_.write(f)
    zip_.close()

    data = zdata.getvalue()
    zip_type = mimetypes.guess_type('dummy.zip')[0]
    headers = [('Content-Type', str(zip_type)),
           ('Cache-Control', 'no-cache'),
           ('Content-Length', str(len(data))),
           ('Content-Disposition', str("attachment; filename=\"%s.%s\"" % 
            (datetime.now(),"zip"))) ]

    return Response(body=data, headerlist=headers)

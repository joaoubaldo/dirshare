import os
import mimetypes
from StringIO import StringIO
import mimetypes
from base64 import b64encode, b64decode
from datetime import datetime

from PIL import Image
import exifread

from dirshare.utils.image import *

RESIZES_COLL = 'resizes'
METADATA_COLL = 'metadata'

#TODO: most of these functions should live inside a model's class


def _dbcoll_resizes(db):
    return db[RESIZES_COLL]

def _dbcoll_metadata(db):
    return db[METADATA_COLL]   


def setup(db):
    _dbcoll_resizes(db).ensure_index([('path', 1)])

def get_all_resizes_from_db(db):
    r = _dbcoll_resizes(db).find()
    return r
    
def remove_all_resizes_from_db(db):
    _dbcoll_resizes(db).remove()


def get_resize_from_db(db, path, size):
    """
    Retrieve a resized image from mongo db.

    @param db: pymongo db instance
    @param path: the image to retrieve
    @param size: the size to retrieve
    @return: the mongo document or None if not found
    """
    r = _dbcoll_resizes(db).find_one(
        {"path": path, 
        "size": size})
    return r


def save_resize_to_db(db, path, size, data, force=False):
    """
    Save a resized image to mongo db.

    @param db: pymongo db instance
    @param path: the image path
    @param size: the size
    @param data: resized image contents
    @param force: if True and path exists on mongo db, the document will be update, otherwise a ValueError exception
    is raised.
    @return: the mongo document
    """
    doc = get_resize_from_db(db, path, size)

    if doc is not None:        
        if not force:
            raise ValueError("Already in db")
    else:
        doc = {}
            
    doc.update({
        'path': path,
        'size': size,
        'mime_type': get_mimetype(path),
        'insert_date': datetime.now(),
        'content': b64encode(data)
    })
    _dbcoll_resizes(db).save(doc)
    return get_resize_from_db(db, path, size)


def get_meta_from_db(db, path):
    """
    Retrieve image meta data from mongo db.

    @param db: the pymongo db instance
    @param path: the image to retrieve
    @return: the mongo document or None if image is not found
    """
    return _dbcoll_metadata(db).find_one({"path": path})


def save_meta_to_db(db, path, force=False):
    """
    Save image meta data to mongo db.

    @param db: the pymongo db instance
    @param path: the image to read
    @param force: if True, meta data will be updated, otherwise, if meta data already exists and this parameter is False
    a ValueError exception is raised.
    @return: the mongo document
    """
    doc = get_meta_from_db(db, path)
    if not force:
        if doc is not None:
            raise ValueError("Already in db")

    f = open(path, 'rb')
    tags = exifread.process_file(f)
    doc = {
        'path': path,
        'exif': {}
        }

    for k, v in tags.iteritems():
        try:
            str(v).decode('utf-8')
            doc['exif'][k] = str(v)
        except UnicodeDecodeError:
            pass

    _dbcoll_metadata(db).save(doc)
    return get_meta_from_db(db, path)

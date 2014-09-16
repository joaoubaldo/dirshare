import os
import mimetypes
from StringIO import StringIO
import mimetypes
from base64 import b64encode, b64decode
from datetime import datetime

from PIL import Image
import exifread

def sizestring_to_tuple(s):
    """
    Converts size representation string WIDTHxHEIGHT to a tuple (width, height)

    @param s: is the size string
    @return: a tuple as (width, height)
    """
    return tuple([int(d) for d in s.split('x')])


def resize(path, size, format_, quality):
    """
    Resize an image file in memory, returning the resized version content.

    @param path: is the path to the image file
    @param size: size string with WIDTHxHEIGHT syntax (ex. "900x900")
    @param format_: is the encoder to use (ex. "JPEG")
    @param quality: quality setting to pass to encoder (ex. 95)
    @return: the resized image content
    """
    f = Image.open(path, 'r')
    f.thumbnail(sizestring_to_tuple(size), Image.ANTIALIAS)
    data_ = StringIO()
    f.save(fp=data_, format=format_, quality=quality)
    return data_.getvalue()


def rotate_data(data, angle, format_, quality):
    f = Image.open(StringIO(data), 'r')
    f = f.rotate(angle)
    data_ = StringIO()
    f.save(fp=data_, format=format_, quality=quality)
    return data_.getvalue()


def get_mimetype(path):
    """
    Get the mime type string for a specific file

    @param path: the file name to read.
    @return: a string with the mime type (ex. "image/jpeg")
    """
    return mimetypes.guess_type(path)[0]


def is_valid_image(path):
    """
    Checks if path is an image file.

    @param path: is the image file to check.
    @return: True if path is an image, False otherwise.
    """
    valid = ['image/gif', 'image/jpeg', 'image/png']
    mt = mimetypes.guess_type(path)
    return os.path.isfile(path) and mt[0] and mt[0] in valid


def read_exif(path):
    """
    Reads exif tags into a dict.

    @param path: is the file path to read
    @return: a dict with exif tags
    """
    f = open(path, 'r')
    tags = exifread.process_file(f)
    exif = {}
    for k, v in tags.iteritems():
        try:
            str(v).decode('utf-8')
            exif[k] = str(v)
        except UnicodeDecodeError:
            pass

    return exif

def process_resize_jobs(db, job_names):
    """
    Batch process a list of resize jobs.

    @param db: IDataAccess instance
    @param job_names: list of job names
    """
    for j in job_names:
        job = db.get_job(j)
        if job['options']['what'] == 'thumbs_meta':
            data = resize(
                job['options']['path'],
                job['options']['sizes'][0],
                job['options']['format'],
                job['options']['quality'])

            db.save_resize(job['options']['path'],
                           job['options']['sizes'][0],
                           data,
                           get_mimetype(
                               "dummy.%s" % (job['options']['format'],)),
                           force=True)

            db.save_metadata(job['options']['path'],
                read_exif(job['options']['path']),
                get_mimetype(job['options']['path']),
                force=True)
            db.remove_job(j)
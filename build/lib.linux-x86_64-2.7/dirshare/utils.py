""" This module contains a collection of usefull functions used by dirshare """

import os
import mimetypes
from StringIO import StringIO

from PIL import Image

def get_dir_contents(path, sorted_=True, only=None):
    """
    Generate a list of directory images and subdirectories.

    @param path is the path name.
    @param sorted_ is a boolean indicating whether or not to sort the resulting
        list elements.
    @param only is 'd' to return directories only, 'f' for files only, None
        for everything.
    @returns a list of tuples. Each tuple contains a boolean indicating if the 
        file is a directory and file name.
    """
    contents = []
    for c in os.listdir(path):
        f = "%s/%s" % (path, c)
        mt = mimetypes.guess_type(f)
        if os.path.isfile(f) and mt[0] and mt[0].startswith('image') \
        and only != 'd':
            contents.append((False, c))
        elif os.path.isdir(f) and only != 'f':
            contents.append((True, c))

    if sorted_:
        contents = sorted(contents, key=lambda i: i[1])

    return contents


def sizestring_to_tuple(s):
    """
    Converts size representation string WIDTHxHEIGHT to a tuple (width, height)

    @param s is the size string
    @returns a tuple as (width, height)
    """
    return tuple([int(d) for d in s.split('x')])


def build_path_breadcrumb(path):
    """
    Generates a list of tuples as (parent_dir, file_name). 
    First list element contains None as parent_dir.

    @param path is the path string to process
    @returns a list of tuples as (parent_dir, file_name)

    Ex.
        build_path_breadcrumb("/images/foo/bar.jpg")

        returns
        [(None, 'images'), ('images', 'foo'), ('images/foo', 'bar.jpg')]
    """
    if path.startswith('/'):
        path = path[1:]
    l = []
    res = []
    for d in path.split('/'):
        res.append( ('/'.join(l) if l else None, d) )
        l.append(d)
    return res


def stream_image(path, scale=None, format_="JPEG", quality=90):
    """
    For a specific image (path), resize it if needed, get its contents and 
    generate http headers.

    @param path is the image path
    @param scale is a tuple containing (max_width, max_height) or None if no 
        resizing should be performed.
        Image will be resized with its aspect ratio kept.
    @param format_ is the image encoder to use when resizing.
    @param quality is the quality parameter passed to image encoder.
    @returns a tuple with (image_data, list_of_http_headers)
    """
    data = ""
    if not scale:
        f = open(path, 'r')
        data = f.read()
    else:
        f = Image.open(path, 'r')
        new_size = ratio_resize(f.size, scale)
        data_ = StringIO()
        f.resize(new_size, Image.ANTIALIAS).save(fp=data_, format=format_, 
            quality=quality)
        data = data_.getvalue()
    headers = [
        ('Content-Type', mimetypes.guess_type(path)[0]),
        ('Cache-Control', 'no-cache'),
        ('Content-Length', str(len(data)))
    ]

    return (data, headers)


def ratio_resize(original, desired):
    """
    Calculate final width and height based on original size and desired 
    maximums.

    @param original is a tuple containing the original (width, height).
    @param desired is a tuple containing (max_width, max_height).
    @returns a tuple with calculated (width, height) or False if desired 
        dimensions are bigger than original's.
    """
    highest = 0   # assume width """
    lowest = 1   # assume height """
    equal = False
    if original[0] < original[1]:
        highest = 1
        lowest = 0
    elif original[0] == original[1]:
        equal = True

    ns = list(desired)

    # Is width == height?
    if equal and (ns[0] > 0):
        ns[1] = ns[0]
    elif equal and (ns[1] > 0):
        ns[0] = ns[1]

    # Does given width/height contain a valid value?
    elif (ns[highest] > 0):
        ns[lowest] = (original[lowest] * ns[highest]) / original[highest]
    elif (ns[lowest] > 0):
        ns[highest] = (original[highest] * ns[lowest]) / original[lowest]

    # Both width and height are higher than the original or both 0
    else:
        return False
    return ns

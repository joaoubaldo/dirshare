import os
import mimetypes
from StringIO import StringIO

from PIL import Image

"""
"""
def get_dir_contents(path, sorted_=True):
    contents = []
    for c in os.listdir(path):
        f = "%s/%s" % (path, c)
        mt = mimetypes.guess_type(f)
        if os.path.isfile(f) and mt[0] and mt[0].startswith('image'):
            contents.append((False, c))
        elif os.path.isdir(f):
            contents.append((True, c))

    if sorted_:
        contents = sorted(contents, key=lambda i: i[1])

    return contents




"""
Converts string WIDTHxHEIGHT to a tuple (width, height)
"""
def sizestring_to_tuple(s):
    return tuple([int(d) for d in s.split('x')])



"""
Build a list of tuples as:
    [ (parent dir, dir), ... ]
"""
def build_path_breadcrumb(path):
    if path.startswith('/'):
        path = path[1:]
    l = []
    res = []
    for d in path.split('/'):
        res.append( ('/'.join(l) if l else None, d) )
        l.append(d)

    return res

"""
Generate data and headers for image in path.
If scale (tuple: width,height) is not None, image will be resized to this 
maximum size, maintaining aspect ratio.
"""
def stream_image(path, scale=None, format_="JPEG", quality=90):
    data = ""
    if not scale:
        f = open(path, 'r')
        data = f.read()
    else:
        f = Image.open(path, 'r')
        new_size = ratio_resize(f.size, scale)
        data_ = StringIO()
        f.resize(new_size, Image.ANTIALIAS).save(fp=data_, format=format_, quality=quality)
        data = data_.getvalue()

    headers = [
        ('Content-Type', mimetypes.guess_type(path)[0]),
        ('Cache-Control', 'no-cache'),
        ('Content-Length', str(len(data)))
    ]

    return (data, headers)


"""
Calculate final width and height based on original size and desired maximums.
Returns tuple with final width and height
"""
def ratio_resize(original, desired):
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

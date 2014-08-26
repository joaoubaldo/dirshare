import os

from dirshare.utils.image import *

def get_dir_contents(path, sorted_=True, only=None):
    """
    Generate a list of directories, images and subdirectories.

    @param path: is the path name.
    @param sorted_: is a boolean indicating whether or not to sort the resulting
        list elements.
    @param only: is 'd' to return directories only, 'f' for files only, None
        for everything.
    @return: a list of tuples. Each tuple contains a boolean indicating if the
        file is a directory and file name.
    """
    contents = []
    for c in os.listdir(path):
        f = "%s/%s" % (path, c)
        if is_valid_image(f) and only != 'd':
            contents.append((False, c))
        elif os.path.isdir(f) and only != 'f':
            contents.append((True, c))

    if sorted_:
        contents = sorted(contents, key=lambda i: i[1])

    return contents


def build_path_breadcrumb(path):
    """
    Generates a list of tuples as (parent_dir, file_name). 
    First list element contains None as parent_dir.

    @param path: is the path string to process
    @return: a list of tuples as (parent_dir, file_name)

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

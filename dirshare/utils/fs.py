import os

from dirshare.utils.image import *

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
    if path.endswith('/'):
        path = path[:-1]

    for d in path.split('/'):
        res.append( ('/'.join(l) if l else None, d) )
        l.append(d)
    return res

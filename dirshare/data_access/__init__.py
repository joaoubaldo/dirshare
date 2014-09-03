class IDirshareDataAccess:
    '''
    Interface class for Dirshare data access, namely, resizes and metadata.
    '''
    def __init__(self, uri):
        '''
        Constructor.

        @param uri: uri string
        @return: instance
        '''
        self.uri = uri

    def setup(self):
        '''
        Sets up initial state.
        '''
        raise NotImplementedError

    def get_resizes(self):
        '''
        Get all resizes from db.

        @return: a collection of dicts representing resizes
        '''
        raise NotImplementedError

    def get_resize(self, path, size):
        '''
        Get a resize from db.

        @param path: file name path string
        @param size: size string
        @return: a dict representing the resize
        '''
        raise NotImplementedError

    def remove_resizes(self):
        '''
        Remove all resizes.
        '''
        raise NotImplementedError

    def remove_resize(self, path, size=None):
        '''
        Remove a resize.

        @param path: file name path string
        @param size: resize size string
        '''
        raise NotImplementedError

    def save_resize(self, path, size, data, mimetype, force=False):
        '''
        Save a resize to db.

        @param path: file name path string
        @param size: size string
        @param data: binary data
        @param mimetype: mime type string
        @param force: if True, resize will be overwritten if already exists
        '''
        raise NotImplementedError

    def get_metadata(self, path):
        '''
        Get metadata from db.

        @param path: file name path string
        @return: a dict representing metadata
        '''
        raise NotImplementedError

    def get_all_metadata(self):
        '''
        Get all metadata from db.

        @return: a collection of dict's representing all metadata
        '''
        raise NotImplementedError

    def save_metadata(self, path, metadata, mimetype, force=False):
        '''
        Save metadata to db.

        @param path: file name path string
        @param mimetype: mime type string
        @param force: when True, metadata will be overwritten if already exists
        '''
        raise NotImplementedError

    def remove_metadata(self, path):
        '''
        Removes metadata for a file.

        @param path: file name path string
        '''
        raise NotImplementedError

    def remove_all_metadata(self):
        '''
        Removes all metadata from db.
        '''
        raise NotImplementedError



def data_access_factory(uri):
    '''
    Creates an instance of a specific DataAcess class based on URI.

    @param uri: uri string with connection information
    @return: a IDirshareDataAccess concrete instance
    '''
    from mongo_access import MongoAccess
    from lite_access import LiteAccess

    try:
        # for python 2
        from urlparse import urlparse
    except ImportError:
        # for python 3
        from urllib.parse import urlparse

    db = urlparse(uri)
    if db.scheme == 'mongodb':
        return MongoAccess(uri)
    elif db.scheme == 'sqlite':
        return LiteAccess(uri)
    else:
        raise ValueError("Invalid scheme")

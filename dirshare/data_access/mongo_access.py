from base64 import b64decode, b64encode
from datetime import datetime

try:
    # for python 2
    from urlparse import urlparse
except ImportError:
    # for python 3
    from urllib.parse import urlparse

from pymongo.mongo_client import MongoClient

from dirshare.data_access import IDirshareDataAccess
from dirshare import utils


class MongoAccess (IDirshareDataAccess):
    '''
    MongoDB implementation of IDirshareDataAccess.
    '''
    __resizestable__ = 'resizes'
    __metadatatable__ = 'metadata'

    def setup(self):
        db = urlparse(self.uri)

        self._client = MongoClient(db.hostname, db.port)
        self._db = getattr(self._client, db.path[1:])

        self._db[self.__resizestable__].ensure_index( [('path', 1), ('size', 1)], unique=True)
        self._db[self.__metadatatable__].ensure_index( [('path', 1)], unique=True )


    def get_resizes(self):
        return self._db[self.__resizestable__].find()

    def get_resize(self, path, size):
        return self._db[self.__resizestable__].find_one({
            "path": path,
            "size": size}
        )

    def remove_resizes(self):
        self._db[self.__resizestable__].remove()

    def remove_resize(self, path, size=None):
        if size is None:
            self._db[self.__resizestable__].remove({
            "path": path})
        else:
            self._db[self.__resizestable__].remove({
                "path": path,
                "size": size})

    def save_resize(self, path, size, data, mimetype, force=False):
        doc = self.get_resize(path, size)

        if doc is not None:
            if not force:
                raise ValueError("Already exists")

        if doc is None:
            doc = {}

        doc.update({
            'path': path,
            'size': size,
            'mimetype': mimetype,
            'insert_date': datetime.now(),
            'content': b64encode(data)
        })

        self._db[self.__resizestable__].save(doc)

    def get_metadata(self, path):
        return self._db[self.__metadatatable__].find_one({
            "path": path
        })

    def get_all_metadata(self):
        return self._db[self.__metadatatable__].find()

    def save_metadata(self, path, metadata, mimetype, force=False):
        doc = self.get_metadata(path)

        if not force:
            if doc is not None:
                raise ValueError("Already exists")

        if doc is None:
            doc = {}

        doc.update({
            'path': path,
            'mimetype': mimetype,
            'metadata': metadata
        })

        self._db[self.__metadatatable__].save(doc)

    def remove_metadata(self, path):
        self._db[self.__metadatatable__].remove({
            "path": path
        })

    def remove_all_metadata(self):
        self._db[self.__metadatatable__].remove()
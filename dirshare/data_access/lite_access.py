import sqlite3
from datetime import datetime
from base64 import b64encode
import json

try:
    # for python 2
    from urlparse import urlparse
except ImportError:
    # for python 3
    from urllib.parse import urlparse

from dirshare.data_access import IDirshareDataAccess

class LiteAccess (IDirshareDataAccess):
    __resizestable__ = 'resizes'
    __metadatatable__ = 'metadata'

    def get_all_metadata(self):
        c = self._client.cursor()
        c.execute('SELECT * FROM %s' % (self.__metadatatable__,))
        return c.fetchall()

    def get_resize(self, path, size):
        c = self._client.cursor()
        c.execute('SELECT * FROM %s WHERE path=? and size=?' % (self.__resizestable__,),
              (path, size))
        row = c.fetchone()
        res = None
        if row:
            res = {}
            for k in row.keys():
                res[k] = row[k]
        return res

    def save_resize(self, path, size, data, mimetype, force=False):
        doc = self.get_resize(path, size)
        if doc is not None and not force:
            raise ValueError("Already exists")

        c = self._client.cursor()
        if force and doc is not None:
            c.execute('UPDATE %s SET insert_date=?, content=?, mimetype=?' \
                      'WHERE path=? and size=?' % (self.__resizestable__,),
                (datetime.now(), b64encode(data), mimetype, path, size))
        else:
            c.execute('INSERT INTO %s (path, insert_date, size, content, mimetype)' \
                      'VALUES (?,?,?,?,?)' % (self.__resizestable__,),
                (path, datetime.now(), size, b64encode(data), mimetype))
        self._client.commit()

    def remove_resize(self, path, size=None):
        c = self._client.cursor()
        c.execute('DELETE FROM %s WHERE path = ? AND size = ?' % (self.__resizestable__,), (path, size))
        self._client.commit()

    def setup(self):
        db = urlparse(self.uri)
        path = ''
        if db.netloc != '':
            path = db.netloc
        elif db.path != '':
            path = db.path
        else:
            raise ValueError("Invalid db path")

        self._client = sqlite3.connect(path)
        self._client.row_factory = sqlite3.Row
        c = self._client.cursor()
        try:
            c.execute("create table %s (path text, insert_date text, content text, mimetype text, size text)" % (
                self.__resizestable__, ))
        except sqlite3.OperationalError:
            pass

        try:
            c.execute("create table %s (path text, mimetype text, metadata text)" % (
                self.__metadatatable__, ))
        except sqlite3.OperationalError:
            pass
        self._client.commit()

    def remove_metadata(self, path):
        c = self._client.cursor()
        c.execute('DELETE FROM %s WHERE path = ?' % (self.__metadatatable__,), (path,))
        self._client.commit()

    def get_metadata(self, path):
        c = self._client.cursor()
        c.execute('SELECT * FROM %s WHERE path=?' % (self.__metadatatable__,),
              (path,))
        row = c.fetchone()
        res = None
        if row:
            res = {}
            for k in row.keys():
                v = row[k]
                if k in ('metadata',):
                    res[k] = json.loads(v)
                else:
                    res[k] = v
        return res

    def remove_resizes(self):
        c = self._client.cursor()
        c.execute('DELETE FROM %s' % (self.__resizestable__,))
        self._client.commit()

    def remove_all_metadata(self):
        c = self._client.cursor()
        c.execute('DELETE FROM %s' % (self.__metadatatable__,))
        self._client.commit()

    def save_metadata(self, path, metadata, mimetype, force=False):
        doc = self.get_metadata(path)
        if doc is not None and not force:
            raise ValueError("Already exists")

        c = self._client.cursor()
        if force and doc is not None:
            c.execute('UPDATE %s SET mimetype=?, metadata=?' \
                      'WHERE path=?' % (self.__metadatatable__,),
                (mimetype, json.dumps(metadata), path))
        else:
            c.execute('INSERT INTO %s (path, mimetype, metadata)' \
                      'VALUES (?,?,?)' % (self.__metadatatable__,),
                (path, mimetype, json.dumps(metadata)))
        self._client.commit()

    def get_resizes(self):
        c = self._client.cursor()
        c.execute('SELECT * FROM %s' % (self.__resizestable__,))
        return c.fetchall()
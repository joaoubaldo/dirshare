import sqlite3
from datetime import datetime
from base64 import b64encode
import json
from threading import Lock

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
    _c = None  # single sqlite3 connection instance
    _c_lock = None  # _c lock

    def get_all_metadata(self):
        LiteAccess._c_lock.acquire()
        c = LiteAccess._c.cursor()
        c.execute('SELECT * FROM %s' % (self.__metadatatable__,))
        r = c.fetchall()
        LiteAccess._c_lock.release()
        return r

    def get_resize(self, path, size):
        LiteAccess._c_lock.acquire()
        c = LiteAccess._c.cursor()
        c.execute('SELECT * FROM %s WHERE path=? and size=?' % (self.__resizestable__,),
              (path, size))
        row = c.fetchone()
        res = None
        if row:
            res = {}
            for k in row.keys():
                res[k] = row[k]
        LiteAccess._c_lock.release()
        return res

    def save_resize(self, path, size, data, mimetype, force=False):
        doc = self.get_resize(path, size)
        LiteAccess._c_lock.acquire()
        if doc is not None and not force:
            raise ValueError("Already exists")

        c = LiteAccess._c.cursor()
        if force and doc is not None:
            c.execute('UPDATE %s SET insert_date=?, content=?, mimetype=?' \
                      'WHERE path=? and size=?' % (self.__resizestable__,),
                (datetime.now(), b64encode(data), mimetype, path, size))
        else:
            c.execute('INSERT INTO %s (path, insert_date, size, content, mimetype)' \
                      'VALUES (?,?,?,?,?)' % (self.__resizestable__,),
                (path, datetime.now(), size, b64encode(data), mimetype))
        LiteAccess._c.commit()
        LiteAccess._c_lock.release()

    def remove_resize(self, path, size=None):
        c = LiteAccess._c.cursor()
        c.execute('DELETE FROM %s WHERE path = ? AND size = ?' % (self.__resizestable__,), (path, size))
        LiteAccess._c.commit()

    def setup(self):
        db = urlparse(self.uri)
        path = ''
        if db.netloc != '':
            path = db.netloc
        elif db.path != '':
            path = db.path
        else:
            raise ValueError("Invalid db path")

        if LiteAccess._c is None:
            LiteAccess._c = sqlite3.connect(path, check_same_thread=False)
            LiteAccess._c_lock = Lock()
            LiteAccess._c_lock.acquire()
            LiteAccess._c.row_factory = sqlite3.Row
            LiteAccess._c_lock.release()

        LiteAccess._c_lock.acquire()
        c = LiteAccess._c.cursor()
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
        LiteAccess._c.commit()
        LiteAccess._c_lock.release()

    def remove_metadata(self, path):
        LiteAccess._c_lock.acquire()
        c = LiteAccess._c.cursor()
        c.execute('DELETE FROM %s WHERE path = ?' % (self.__metadatatable__,), (path,))
        LiteAccess._c.commit()
        LiteAccess._c_lock.release()

    def get_metadata(self, path):
        LiteAccess._c_lock.acquire()
        c = LiteAccess._c.cursor()
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
        LiteAccess._c_lock.release()
        return res

    def remove_resizes(self):
        LiteAccess._c_lock.acquire()
        c = LiteAccess._c.cursor()
        c.execute('DELETE FROM %s' % (self.__resizestable__,))
        LiteAccess._c.commit()
        LiteAccess._c_lock.release()

    def remove_all_metadata(self):
        LiteAccess._c_lock.acquire()
        c = LiteAccess._c.cursor()
        c.execute('DELETE FROM %s' % (self.__metadatatable__,))
        LiteAccess._c.commit()
        LiteAccess._c_lock.release()

    def save_metadata(self, path, metadata, mimetype, force=False):
        doc = self.get_metadata(path)
        LiteAccess._c_lock.acquire()
        if doc is not None and not force:
            raise ValueError("Already exists")

        c = LiteAccess._c.cursor()
        if force and doc is not None:
            c.execute('UPDATE %s SET mimetype=?, metadata=?' \
                      'WHERE path=?' % (self.__metadatatable__,),
                (mimetype, json.dumps(metadata), path))
        else:
            c.execute('INSERT INTO %s (path, mimetype, metadata)' \
                      'VALUES (?,?,?)' % (self.__metadatatable__,),
                (path, mimetype, json.dumps(metadata)))
        LiteAccess._c.commit()
        LiteAccess._c_lock.release()

    def get_resizes(self):
        LiteAccess._c_lock.acquire()
        c = LiteAccess._c.cursor()
        c.execute('SELECT * FROM %s' % (self.__resizestable__,))
        r = c.fetchall()
        LiteAccess._c_lock.release()
        return r

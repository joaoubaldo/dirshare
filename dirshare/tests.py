import unittest
import logging
import os
import sys
from base64 import b64decode

from pyramid import testing
from pyramid.request import Request
from pymongo.mongo_client import MongoClient


class ViewTests(unittest.TestCase):

    def setdb(self, scheme):
        from .data_access import data_access_factory

        if scheme == 'mongodb':
            self.db = data_access_factory("mongodb://127.0.0.1:27017/dirshare_test")
        elif scheme == 'sqlite':
            self.db = data_access_factory("sqlite://:memory:")
        self.log.info("Using %s data access" % (scheme,) )
        self.db.setup()
        self.db.remove_resizes()
        self.db.remove_all_metadata()

    def setUp(self):
        from . import utils

        logging.basicConfig( stream=sys.stderr )
        logging.getLogger( "dirshare.tests" ).setLevel( logging.DEBUG )
        self.log = logging.getLogger( "dirshare.tests" )

        settings = {
            'image_sizes': "128x128 600x600 full",
            'images_per_page': 10,
            'images_root': '/',
            'resize_quality': 50,
            'resize_format': "JPEG",
        }

        self.config = testing.setUp(settings=settings)
        self.img_data =\
        '''/9j/4AAQSkZJRgABAQEAtAC0AAD/4QiYRXhpZgAASUkqAAgAAAAJAA8BAgAGAAAAegAAABABAgAU
AAAAgAAAABIBAwABAAAAAQAAABoBBQABAAAAlAAAABsBBQABAAAAnAAAACgBAwABAAAAAgAAADIB
AgAUAAAApAAAABMCAwABAAAAAQAAAGmHBAABAAAAuAAAALIFAABDYW5vbgBDYW5vbiBQb3dlclNo
b3QgUzQwALQAAAABAAAAtAAAAAEAAAAyMDE0OjA4OjI1IDE0OjU5OjE3AB8AmoIFAAEAAAAyAgAA
nYIFAAEAAAA6AgAAAJAHAAQAAAAwMjIwA5ACABQAAABCAgAABJACABQAAABWAgAAAZEHAAQAAAAB
AgMAApEFAAEAAABqAgAAAZIKAAEAAAByAgAAApIFAAEAAAB6AgAABJIKAAEAAACCAgAABZIFAAEA
AACKAgAAB5IDAAEAAAACAAAACZIDAAEAAAAYAAAACpIFAAEAAACSAgAAfJIHAMIBAACaAgAAhpIH
AAgBAABcBAAAAKAHAAQAAAAwMTAwAaADAAEAAAABAAAAAqADAAEAAAAMAAAAA6ADAAEAAAAJAAAA
BaAEAAEAAAB8BQAADqIFAAEAAABkBQAAD6IFAAEAAABsBQAAEKIDAAEAAAACAAAAF6IDAAEAAAAC
AAAAAKMHAAEAAAADAAAAAaQDAAEAAAAAAAAAAqQDAAEAAAAAAAAAA6QDAAEAAAAAAAAABKQFAAEA
AAB0BQAABqQDAAEAAAAAAAAAAAAAAAEAAAD0AQAAMQAAAAoAAAAyMDAzOjEyOjE0IDEyOjAxOjQ0
ADIwMDM6MTI6MTQgMTI6MDE6NDQABQAAAAEAAAAfAQAAIAAAAJUAAAAgAAAAAAAAAAMAAACK+AIA
AAABAKoCAAAgAAAADAABAAMAKAAAADADAAACAAMABAAAAIADAAADAAMABAAAAIgDAAAEAAMAGwAA
AJADAAAAAAMABgAAAMYDAAAAAAMABAAAANIDAAAGAAIAIAAAANoDAAAHAAIAGAAAAPoDAAAIAAQA
AQAAADvhEQAJAAIAIAAAABIEAAAQAAQAAQAAAAAAEQENAAMAFQAAADIEAAAAAAAAUAACAAAABQAB
AAAAAAAEAAAAAQAAAAEAAAAAAAAAAAARAAUAAQADMAEA/////6oC4wAgAJUAwAAAAAAAAAAAAAAA
AAD//zEA4AjgCAAAAQACAKoCHgHXAAAAAAAAAAAANgAAAKAAFAGVAB8BAAAAAAAAAAAGAAAAAAAA
AAIwAAAAAAAAAQAOAwAAlQAhAQAAAAAAAPoAAAAAAAAAAAAAAAAAAAAAAAAAAABJTUc6UG93ZXJT
aG90IFM0MCBKUEVHAAAAAAAAAAAAAEZpcm13YXJlIFZlcnNpb24gMS4xMAAAAEFuZHJlYXMgSHVn
Z2VsAAAAAAAAAAAAAAAAAAAAAAAAKgADAAGAegEBgAAAAAAAAAMBAgAAAAoAAAAAAAAAOQDGAAUA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKsiABgBAABAABoA0gAA
AOAIAADgCAAABAABAAIABAAAAFI5OAACAAcABAAAADAxMDABEAMAAQAAAOAIAAACEAMAAQAAAKgG
AAAAAAAABgADAQMAAQAAAAYAAAAaAQUAAQAAAAAGAAAbAQUAAQAAAAgGAAAoAQMAAQAAAAIAAAAB
AgQAAQAAABAGAAACAgQAAQAAAIACAAAAAAAAtAAAAAEAAAC0AAAAAQAAAP/Y/+AAEEpGSUYAAQEA
AAEAAQAA/9sAQwBQNzxGPDJQRkFGWlVQX3jIgnhubnj1r7mRyP//////////////////////////
/////////////////////////9sAQwFVWlp4aXjrgoLr////////////////////////////////
/////////////////////////////////////////8AAEQgABgAJAwEiAAIRAQMRAf/EAB8AAAEF
AQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFB
BhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RV
VldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrC
w8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAA
AAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRC
kaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdo
aWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT
1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8AhjEP7zchPPy+361BRRQB/9n/
4QtuaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLwA8P3hwYWNrZXQgYmVnaW49J++7vycgaWQ9
J1c1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCc/Pgo8eDp4bXBtZXRhIHhtbG5zOng9J2Fkb2JlOm5z
Om1ldGEvJz4KPHJkZjpSREYgeG1sbnM6cmRmPSdodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIy
LXJkZi1zeW50YXgtbnMjJz4KCiA8cmRmOkRlc2NyaXB0aW9uIHhtbG5zOmV4aWY9J2h0dHA6Ly9u
cy5hZG9iZS5jb20vZXhpZi8xLjAvJz4KICA8ZXhpZjpNYWtlPkNhbm9uPC9leGlmOk1ha2U+CiAg
PGV4aWY6TW9kZWw+Q2Fub24gUG93ZXJTaG90IFM0MDwvZXhpZjpNb2RlbD4KICA8ZXhpZjpPcmll
bnRhdGlvbj5Ub3AtbGVmdDwvZXhpZjpPcmllbnRhdGlvbj4KICA8ZXhpZjpYUmVzb2x1dGlvbj4x
ODA8L2V4aWY6WFJlc29sdXRpb24+CiAgPGV4aWY6WVJlc29sdXRpb24+MTgwPC9leGlmOllSZXNv
bHV0aW9uPgogIDxleGlmOlJlc29sdXRpb25Vbml0PkluY2g8L2V4aWY6UmVzb2x1dGlvblVuaXQ+
CiAgPGV4aWY6RGF0ZVRpbWU+MjAwMzoxMjoxNCAxMjowMTo0NDwvZXhpZjpEYXRlVGltZT4KICA8
ZXhpZjpZQ2JDclBvc2l0aW9uaW5nPkNlbnRlcmVkPC9leGlmOllDYkNyUG9zaXRpb25pbmc+CiAg
PGV4aWY6Q29tcHJlc3Npb24+SlBFRyBjb21wcmVzc2lvbjwvZXhpZjpDb21wcmVzc2lvbj4KICA8
ZXhpZjpYUmVzb2x1dGlvbj4xODA8L2V4aWY6WFJlc29sdXRpb24+CiAgPGV4aWY6WVJlc29sdXRp
b24+MTgwPC9leGlmOllSZXNvbHV0aW9uPgogIDxleGlmOlJlc29sdXRpb25Vbml0PkluY2g8L2V4
aWY6UmVzb2x1dGlvblVuaXQ+CiAgPGV4aWY6RXhwb3N1cmVUaW1lPjEvNTAwIHNlYy48L2V4aWY6
RXhwb3N1cmVUaW1lPgogIDxleGlmOkZOdW1iZXI+Zi80LDk8L2V4aWY6Rk51bWJlcj4KICA8ZXhp
ZjpFeGlmVmVyc2lvbj5FeGlmIFZlcnNpb24gMi4yPC9leGlmOkV4aWZWZXJzaW9uPgogIDxleGlm
OkRhdGVUaW1lT3JpZ2luYWw+MjAwMzoxMjoxNCAxMjowMTo0NDwvZXhpZjpEYXRlVGltZU9yaWdp
bmFsPgogIDxleGlmOkRhdGVUaW1lRGlnaXRpemVkPjIwMDM6MTI6MTQgMTI6MDE6NDQ8L2V4aWY6
RGF0ZVRpbWVEaWdpdGl6ZWQ+CiAgPGV4aWY6Q29tcG9uZW50c0NvbmZpZ3VyYXRpb24+CiAgIDxy
ZGY6U2VxPgogICAgPHJkZjpsaT5ZIENiIENyIC08L3JkZjpsaT4KICAgPC9yZGY6U2VxPgogIDwv
ZXhpZjpDb21wb25lbnRzQ29uZmlndXJhdGlvbj4KICA8ZXhpZjpDb21wcmVzc2VkQml0c1BlclBp
eGVsPiA1PC9leGlmOkNvbXByZXNzZWRCaXRzUGVyUGl4ZWw+CiAgPGV4aWY6U2h1dHRlclNwZWVk
VmFsdWU+OCw5NyBFViAoMS81MDEgc2VjLik8L2V4aWY6U2h1dHRlclNwZWVkVmFsdWU+CiAgPGV4
aWY6QXBlcnR1cmVWYWx1ZT40LDY2IEVWIChmLzUsMCk8L2V4aWY6QXBlcnR1cmVWYWx1ZT4KICA8
ZXhpZjpFeHBvc3VyZUJpYXNWYWx1ZT4wLDAwIEVWPC9leGlmOkV4cG9zdXJlQmlhc1ZhbHVlPgog
IDxleGlmOk1heEFwZXJ0dXJlVmFsdWU+Miw5NyBFViAoZi8yLDgpPC9leGlmOk1heEFwZXJ0dXJl
VmFsdWU+CiAgPGV4aWY6TWV0ZXJpbmdNb2RlPkNlbnRlci13ZWlnaHRlZCBhdmVyYWdlPC9leGlm
Ok1ldGVyaW5nTW9kZT4KICA8ZXhpZjpGbGFzaCByZGY6cGFyc2VUeXBlPSdSZXNvdXJjZSc+CiAg
PC9leGlmOkZsYXNoPgogIDxleGlmOkZvY2FsTGVuZ3RoPjIxLDMgbW08L2V4aWY6Rm9jYWxMZW5n
dGg+CiAgPGV4aWY6TWFrZXJOb3RlPjQ1MCBieXRlcyB1bmRlZmluZWQgZGF0YTwvZXhpZjpNYWtl
ck5vdGU+CiAgPGV4aWY6VXNlckNvbW1lbnQgLz4KICA8ZXhpZjpGbGFzaFBpeFZlcnNpb24+Rmxh
c2hQaXggVmVyc2lvbiAxLjA8L2V4aWY6Rmxhc2hQaXhWZXJzaW9uPgogIDxleGlmOkNvbG9yU3Bh
Y2U+c1JHQjwvZXhpZjpDb2xvclNwYWNlPgogIDxleGlmOlBpeGVsWERpbWVuc2lvbj4yMjcyPC9l
eGlmOlBpeGVsWERpbWVuc2lvbj4KICA8ZXhpZjpQaXhlbFlEaW1lbnNpb24+MTcwNDwvZXhpZjpQ
aXhlbFlEaW1lbnNpb24+CiAgPGV4aWY6Rm9jYWxQbGFuZVhSZXNvbHV0aW9uPjgxMTQsMjg2PC9l
eGlmOkZvY2FsUGxhbmVYUmVzb2x1dGlvbj4KICA8ZXhpZjpGb2NhbFBsYW5lWVJlc29sdXRpb24+
ODExNCwyODY8L2V4aWY6Rm9jYWxQbGFuZVlSZXNvbHV0aW9uPgogIDxleGlmOkZvY2FsUGxhbmVS
ZXNvbHV0aW9uVW5pdD5JbmNoPC9leGlmOkZvY2FsUGxhbmVSZXNvbHV0aW9uVW5pdD4KICA8ZXhp
ZjpTZW5zaW5nTWV0aG9kPk9uZS1jaGlwIGNvbG9yIGFyZWEgc2Vuc29yPC9leGlmOlNlbnNpbmdN
ZXRob2Q+CiAgPGV4aWY6RmlsZVNvdXJjZT5EU0M8L2V4aWY6RmlsZVNvdXJjZT4KICA8ZXhpZjpD
dXN0b21SZW5kZXJlZD5Ob3JtYWwgcHJvY2VzczwvZXhpZjpDdXN0b21SZW5kZXJlZD4KICA8ZXhp
ZjpFeHBvc3VyZU1vZGU+QXV0byBleHBvc3VyZTwvZXhpZjpFeHBvc3VyZU1vZGU+CiAgPGV4aWY6
V2hpdGVCYWxhbmNlPkF1dG8gd2hpdGUgYmFsYW5jZTwvZXhpZjpXaGl0ZUJhbGFuY2U+CiAgPGV4
aWY6RGlnaXRhbFpvb21SYXRpbz4xLDAwMDA8L2V4aWY6RGlnaXRhbFpvb21SYXRpbz4KICA8ZXhp
ZjpTY2VuZUNhcHR1cmVUeXBlPlN0YW5kYXJkPC9leGlmOlNjZW5lQ2FwdHVyZVR5cGU+CiAgPGV4
aWY6SW50ZXJvcGVyYWJpbGl0eUluZGV4PlI5ODwvZXhpZjpJbnRlcm9wZXJhYmlsaXR5SW5kZXg+
CiAgPGV4aWY6SW50ZXJvcGVyYWJpbGl0eVZlcnNpb24+MDEwMDwvZXhpZjpJbnRlcm9wZXJhYmls
aXR5VmVyc2lvbj4KICA8ZXhpZjpSZWxhdGVkSW1hZ2VXaWR0aD4yMjcyPC9leGlmOlJlbGF0ZWRJ
bWFnZVdpZHRoPgogIDxleGlmOlJlbGF0ZWRJbWFnZUxlbmd0aD4xNzA0PC9leGlmOlJlbGF0ZWRJ
bWFnZUxlbmd0aD4KIDwvcmRmOkRlc2NyaXB0aW9uPgoKPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4K
PD94cGFja2V0IGVuZD0ncic/Pgr/2wBDAFA3PEY8MlBGQUZaVVBfeMiCeG5uePWvuZHI////////
////////////////////////////////////////////2wBDAVVaWnhpeOuCguv/////////////
////////////////////////////////////////////////////////////wgARCAAJAAwDAREA
AhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAgD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/9oADAMB
AAIQAxAAAAEBCR//xAAXEAEAAwAAAAAAAAAAAAAAAAABEBEi/9oACAEBAAEFAg0lMf/EABQRAQAA
AAAAAAAAAAAAAAAAACD/2gAIAQMBAT8BH//EABQRAQAAAAAAAAAAAAAAAAAAACD/2gAIAQIBAT8B
H//EABUQAQEAAAAAAAAAAAAAAAAAABEg/9oACAEBAAY/AiP/xAAYEAEAAwEAAAAAAAAAAAAAAAAB
ABARUf/aAAgBAQABPyE1cTZC/wD/2gAMAwEAAgADAAAAEJJP/8QAFBEBAAAAAAAAAAAAAAAAAAAA
IP/aAAgBAwEBPxAf/8QAFBEBAAAAAAAAAAAAAAAAAAAAIP/aAAgBAgEBPxAf/8QAGRABAQADAQAA
AAAAAAAAAAAAEQEAEFFx/9oACAEBAAE/EKqtEHuSZE7v/9k='''

    def tearDown(self):
        testing.tearDown()

    def test_view_ajax_home(self):
        from .views import view_ajax_home

        self.log.info("home view")
        for scheme in ('sqlite', 'mongodb'):
            self.setdb(scheme)
            request = testing.DummyRequest()
            info = view_ajax_home(request)
            self.assertEqual(info, {})


    def test_view_ajax_listdir(self):
        from .views import view_ajax_listdir
        from .views import view_stream_image
        from . import utils
        import tempfile

        self.log.info("list dir view")
        for scheme in ('sqlite', 'mongodb'):
            self.setdb(scheme)
            d = tempfile.mkdtemp()
            for i in range(11):
                f = open(os.path.join(d, "%d.jpg" % (i,)), 'w')
                f.write(b64decode(self.img_data))
                f.close()

            request = testing.DummyRequest()

            request.params['d'] = d
            request.params['p'] = 0
            info = view_ajax_listdir(request)
            self.assertEqual(len(info['files']), 10)

            request.params['d'] = d
            request.params['p'] = 1
            info = view_ajax_listdir(request)
            self.assertEqual(len(info['files']), 1)

            self.assertEqual(info['image_count'], 11)

            self.assertEqual(len(info['pages']), 2)

            request.params['d'] = d
            request.params['p'] = 0
            request.params['pp'] = 9999
            info = view_ajax_listdir(request)
            self.assertEqual(len(info['files']), 11)

            """
            Force cache
            """
            for file_ in info['files']  :
                frequest = testing.DummyRequest()
                frequest.params['d'] = os.path.join(info['path'], file_['name'])
                frequest.matchdict['size'] = "128x128"
                frequest.db = self.db
                view_stream_image(frequest)

            files_db = list(self.db.get_resizes())
            self.assertEqual(len(files_db), 11)


    def test_data_access(self):
        from .data_access import data_access_factory
        from .utils import image
        import tempfile
        import exifread

        self.log.info("data access")
        files = [('test1.jpg' ), ('test2.png' ), ('test3.jpg' )]
        sizes = ['128x128', '600x600', '1000x1000']
        for scheme in ('sqlite', 'mongodb'):
            self.setdb(scheme)
            d = tempfile.mkdtemp()  # make temp dir

            for fname in files:
                path = os.path.join(d, fname)
                f = open(path, 'w')
                f.write(b64decode(self.img_data))  # create temp image file
                f.close()
                self.db.save_metadata(path, image.read_exif(path), image.get_mimetype(fname))
                self.db.save_metadata(path, image.read_exif(path), image.get_mimetype(fname), force=True)
                self.assertRaises(
                    ValueError,
                    self.db.save_metadata,
                    path, image.read_exif(path), image.get_mimetype(fname))

                self.assertIsNotNone(self.db.get_metadata(path))  # metadata is saved

                for size in sizes:
                    self.db.save_resize(path,
                                   size,
                                   b64decode(self.img_data),
                                   image.get_mimetype(fname))
                    self.db.save_resize(path,
                                   size,
                                   b64decode(self.img_data),
                                   image.get_mimetype(fname), force=True)
                    self.assertRaises(
                        ValueError,
                        self.db.save_resize,
                        path,
                        size,
                        b64decode(self.img_data),
                        image.get_mimetype(fname))

                    self.assertIsNotNone(self.db.get_resize(path,size))  # resize is saved

            self.assertEqual(len(list(self.db.get_resizes())), len(files)*len(sizes))
            self.assertEqual(len(list(self.db.get_all_metadata())), len(files))

            self.db.remove_resizes()
            self.db.remove_all_metadata()
            self.assertEqual(len(list(self.db.get_resizes())), 0)
            self.assertEqual(len(list(self.db.get_all_metadata())), 0)

            # start over, empty db
            for fname in files:
                path = os.path.join(d, fname)
                self.db.save_metadata(path, image.read_exif(path), image.get_mimetype(fname))

                for size in sizes:
                    self.db.save_resize(path,
                                   size,
                                   b64decode(self.img_data),
                                   image.get_mimetype(fname))
                    self.assertIsNotNone(self.db.get_resize(path, size))
                    self.db.remove_resize(path, size)  # remove one resize
                    self.assertIsNone(self.db.get_resize(path, size))

                self.assertIsNotNone(self.db.get_metadata(path))
                self.db.remove_metadata(path)  # remove one metadata
                self.assertIsNone(self.db.get_metadata(path))

            self.assertEqual(len(list(self.db.get_resizes())), 0)
            self.assertEqual(len(list(self.db.get_all_metadata())), 0)



    def test_jobs(self):
        from .data_access import data_access_factory
        from threading import Thread
        from .utils import image
        import tempfile
        import exifread

        self.log.info("jobs")
        what = 'thumbs_meta'
        files = [('test1.jpg' ), ('test2.png' ), ('test3.jpg' )]
        sizes = ['128x128', '600x600', '1000x1000']

        for scheme in ('sqlite', 'mongodb'):
            self.setdb(scheme)
            d = tempfile.mkdtemp()  # make temp dir
            jobs_created = []
            for fname in files:
                path = os.path.join(d, fname)
                f = open(path, 'w')
                f.write(b64decode(self.img_data))  # create temp image file
                f.close()
                options={'what': what,
                         'path': path,
                         'format': 'JPEG',
                         'quality': 35,
                         'sizes': sizes}

                if not self.db.get_job('rebuild-%s-%s' % (what,path,)):
                    self.db.save_job('rebuild-%s-%s' % (what,path,), options)
                    jobs_created.append('rebuild-%s-%s' % (what,path,))

                Thread(target=image.process_resize_jobs, args=(self.db, jobs_created))
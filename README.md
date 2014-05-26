dirshare
========

Description
-----------
**dirshare** is a small WSGI Python application, that comfortably shares (via HTTP) images within a specific root path, leverages thumbnail caching (with MongoDb), instantaneous image resizing and zip file creation.

The motivation to build this application, is that, I have the need to quickly and remotely browse a large collection of photos, only to pick a few of them, however I don't want to have a dedicated web gallery nor I want to modify the original file structure.


Installation
------------

From PyPI:
> pip install dirshare

Or:
> python setup.py install


Requirements
------------
Besides python requirements that setuptools install, a mongo database server is needed.


Configuration
-------------
The configuration file is a Pyramid-style ini file (see example.ini). Apart from server configuration, the following parameters should be configured:
> mongo_host = localhost

> mongo_port = 27017

> mongo_db = dir_db

> images_per_page = 25

> image_sizes = 128x128 600x600 1000x1000 full

> images_root = /path/to/image/root

> resize_format = JPEG

> resize_quality = 85

* _images\_per\_page_ is the maximum number images to display per page. This parameter can be overwritten in HTTP request, with 'pp' GET parameter.  
* _image\_sizes_ is a space separated list of (re)sizes available in a form of MAX\_WIDTHxMAX\_HEIGHT. The image is resized to these values, with its aspect ratio preserved. The first element in _image\_sizes_ is the thumbnail size. Keyword _full_ is the original image.
* _resize\_format_ is the encoder to use in image resizes.
* _resize\_quality_ is the quality parameter used by image encoder.


Usage
-----
    Usage: dirshare [options]

    Options:
      -h, --help            show this help message and exit
      -c CONFIG, --config=CONFIG
                            Server configuration file path
      -r IMAGES_ROOT, --images-root=IMAGES_ROOT
                            Root directory to share (will override config file)



Examples.

Share production.ini's images_root:
> dirshare -c example.ini

Override production.ini's images_root parameter:
> dirshare -c example.ini -r ~/Pictures


Once dirshare is running, point your browser to its port (default 6543).

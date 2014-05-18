dirshare
========

Description
-----------
**dirshare** is a small WSGI Python application, that comfortably shares images within a specific root path, with the added benefit of thumbnail caching (with MongoDb), real-time image resizing and instantaneous zip file creation.

The motivation to build this application, is that, I have the need to quickly and remotely browse a large collection of photos, just to pick a few photos, however I don't want to have a dedicated web gallery nor I want to modify the original file structure.


Installation
------------

> python setup.py install


Requirements
------------
Besides python requirements that setuptools install, a mongo database server is needed.


Configuration
-------------
The configuration file is a Pyramid-style ini file. Apart from server configuration, the following parameters should be configured:
> mongo.host = localhost

> mongo.port = 27017

> mongo.db = dir_db

> images_per_page = 25

> image_sizes = 128x128 600x600 1000x1000 full

> images_root = /path/to/image/root

> resize_format = JPEG

> resize_quality = 85

**Notes:**

_image\_sizes_ is a space separated list of (re)sizes available in a form of MAX\_WIDTHxMAX\_HEIGHT. The image is resized to these values, with its aspect ratio preserved.

The first element in _image\_sizes_ is the thumbnail size. Keyword _full_ is the original image.


Usage
-----
    Usage: dirshare [options]
    
    Options:
       -h, --help            show this help message and exit
       -c CONFIG, --config=CONFIG
                             Server configuration file path
      -d DIRECTORY, --directory=DIRECTORY
                             Shared directory path (will override config file)


Example:
> dirshare -c production.ini -c /home/user/Pictures

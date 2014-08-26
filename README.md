dirshare
========

Description
-----------
**dirshare** is a HTTP WSGI Python application to rapidly share images within 
a specific root path, leverages thumbnail caching (with MongoDb), 
instantaneous image resizing, file meta data extraction and zip file creation.

The motivation to create this application is that occasionally I must browse a 
large collection of photos, WITHOUT a dedicated server software, loading of 
full sized images or modifying original files.


Requirements
------------
- Setuptools (for installing dirshare and its Python dependencies)
- Access to a mongo database server

**Note** Pillow library uses system libraries to decode specific type of files.
If you get "IOError: decoder XXX not available" while loading some images, 
you're probably missing some libraries (ex. libjpeg).

Installation
------------
From PyPI:
> pip install dirshare

Or:
> python setup.py install


Configuration and usage
-----------------------
1) Generate a .ini file:
> dirshare -e <output.ini>

2) Edit generated file and configured as needed (specially _images\_root_ 
and mongo server settings). Most of the settings are self explanatory.

3) Launch server:
> dirshare -c <output.ini>

4) Point a browser to dirshare's port (default 6543).

* _images\_per\_page_ is the maximum number images to display per page. 
This parameter can be overwritten in HTTP request, with 'pp' GET parameter.
* _image\_sizes_ is a space separated list of (re)sizes available in a form 
of MAX\_WIDTHxMAX\_HEIGHT. The image is resized to these values, with its 
aspect ratio preserved. The first element in _image\_sizes_ is the thumbnail 
size. Keyword _full_ is the original image.
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
      -e EXAMPLE_INI, --example-ini=EXAMPLE_INI
                            Create an example ini file

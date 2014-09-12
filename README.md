dirshare
========

Description
-----------
**dirshare** is a HTTP WSGI Python application to rapidly share images within 
a specific root path, leverages thumbnail caching, instantaneous image 
resizing, file meta data extraction and zip file creation.

The motivation to create this application is that occasionally I must browse a 
large collection of photos, WITHOUT a dedicated server software, loading of 
full sized images or modifying original files.


Requirements
------------
- Setuptools (for installing dirshare and its Python dependencies)
- (optional) Access to a mongo database server

**Note** Pillow library uses system libraries to decode specific type of files.
If you get "IOError: decoder XXX not available" while loading some images, 
you're probably missing some libraries (ex. libjpeg).

Installation
------------
From PyPI:
> pip install dirshare

Or:
> python setup.py install



Usage
-----
Usage: dirshare [options]

Options:
  -h, --help            show this help message and exit
  -r IMAGES_ROOT, --images-root=IMAGES_ROOT
                        Root directory to share (default: ".")
  -s IMAGE_SIZES, --image-sizes=IMAGE_SIZES
                        Available sizes as a string (default: "128x128 600x600
                        1000x1000 full")
  -f RESIZE_FORMAT, --resize-format=RESIZE_FORMAT
                        Resize encoder to use (default: "PNG")
  -q RESIZE_QUALITY, --resize-quality=RESIZE_QUALITY
                        Resize quality value to pass to encoder (default: 90)
  -d DB_URI, --db-uri=DB_URI
                        DB uri (default: "mongodb://localhost:27017/dirshare")
  -p HTTP_PORT, --http-port=HTTP_PORT
                        HTTP listen port (default: 6543)
  -b HTTP_IP, --http-ip=HTTP_IP
                        HTTP bind ip (default: "127.0.0.1")


Example:
  dirshare -r /home/myuser -s "128x128 500x500 full" -d "sqlite://:memory:"

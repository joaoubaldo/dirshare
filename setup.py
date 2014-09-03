import os

from setuptools import setup, find_packages

from dirshare import VERSION

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_mako',
    'waitress',
    'pymongo',
    'pillow',
    'exifread'
    ]

setup(name='dirshare',
      version=VERSION,
      description='dirshare',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Joao Coutinho',
      author_email='me at joaoubaldo.com',
      url='http://b.joaoubaldo.com',
      keywords='web pyramid pylons gallery share',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="dirshare",
      entry_points={
        'paste.app_factory': 
            ['main = dirshare:main'],
        'console_scripts':
            ['dirshare = dirshare.cli.start_waitress:main']
        }
      )

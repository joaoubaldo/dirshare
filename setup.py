import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

print find_packages()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    'pymongo'
    ]

setup(name='dirshare',
      version='0.2',
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
      keywords='web pyramid pylons',
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
            ['dirshare = dirshare.cli:main']
        }
      )

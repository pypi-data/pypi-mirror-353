import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


def get_version(version_file):
    ns = {}
    exec(read(version_file), ns)
    return ns['__version__']


setup(
    name='as_models',
    python_requires=">=3.7",
    version=get_version('as_models/version.py'),
    author='Mac Coombe',
    author_email='mac.coombe@csiro.au',
    description='Analysis Services model integration library.',
    keywords='models',
    # TODO: url = 'https://bitbucket.csiro.au/...',
    packages=find_packages(),
    long_description=read('readme.md'),
    install_requires=[
        'flask==2.2.3',
        'Werkzeug>=2.2.2,<3.0.0' # Note Flask 2.2.3 does not support Werkzeug greater than 2.3.7, but doesn't constrain this in its setup.py
    ],
    test_requires=[
        'httpretty==1.1.4',
        'webob==1.8.7',
        'xarray==0.18.0',
        'rpy2==3.3.3'
    ],
    extras_require={
        'r': ['rpy2==3.3.3'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.7+'
    ]
)

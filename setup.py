# encoding: UTF-8

from setuptools import setup, find_packages
from opendatatools import __version__ as ver

setup(
    # Install data files specified in MANIFEST.in file.
    include_package_data=True,
    # package_data={'': ['*.json', '*.css', '*.html']},
    # Package Information
    name='InvestOpenDataTools',
    url='https://github.com/suuuch/InvestOpenData',
    version=ver,
    license='Apache 2.0',
    # information
    description='Open source data tools Fork .',
    long_description="",
    keywords="data,crawler,free",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
    ],
    # install
    install_requires=[
        'beautifulsoup4==4.9.3',
        'bs4==0.0.1',
        'certifi==2020.12.5',
        'chardet==4.0.0',
        'demjson==2.2.4',
        'idna==2.10',
        'numpy==1.19.4',
        'pandas==1.1.5',
        'Pillow==8.0.1',
        'progressbar2==3.53.1',
        'pytesseract==0.3.7',
        'python-dateutil==2.8.1',
        'python-utils==2.4.0',
        'pytz==2020.5',
        'requests==2.25.1',
        'six==1.15.0',
        'soupsieve==2.1',
        'urllib3==1.26.2',
        'xlrd==2.0.1',

    ],
    packages=find_packages(),
    # author
    author='suuuch'
)

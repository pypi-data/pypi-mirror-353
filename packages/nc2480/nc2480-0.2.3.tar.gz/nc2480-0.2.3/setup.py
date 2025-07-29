from setuptools import setup

import sys
sys.path.insert(0,'')
from nc2480.__init__ import __version__

setup(
    name='nc2480',
    version=__version__,
    description='python ncurses 24x80 tui goodies',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/mdcb/python-nc2480',
    author='Matthieu Bec',
    author_email='mdcb808@gmail.com',
    license='GPL-3.0',
    packages=['nc2480'],
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],
)

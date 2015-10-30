#!/usr/bin/env python
#
# Public Domain

"""
CairoSVG - A Simple SVG Converter based on Cairo
================================================

CairoSVG is a SVG converter based on Cairo. It can convert SVG files into PDF,
PostScript and PNG files.

For further information, please visit the `CairoSVG Website
<http://www.cairosvg.org/>`_.

"""

import re
from os import path

from setuptools import setup

init_path = path.join(path.dirname(__file__), 'cairosvg', '__init__.py')
with open(init_path, 'r', encoding='utf-8') as fd:
    VERSION = re.search("VERSION = '([^']+)'", fd.read().strip()).group(1)


# When the version is updated, ``cairosvg.VERSION`` must be modified.
# A new section in the ``NEWS`` file must be added too.
setup(
    name='CairoSVG',
    version=VERSION,
    description='A Simple SVG Converter based on Cairo',
    long_description=__doc__,
    author='Kozea',
    author_email='guillaume.ayoub@kozea.fr',
    url='http://www.cairosvg.org/',
    license='GNU LGPL v3+',
    platforms='Any',
    packages=['cairosvg', 'cairosvg.surface'],
    provides=['cairosvg'],
    install_requires=['cairocffi', 'lxml', 'cssselect', 'pillow', 'tinycss'],
    keywords=['svg', 'cairo', 'pdf', 'png', 'postscript'],
    entry_points={'console_scripts': 'cairosvg=cairosvg:main'},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion'])

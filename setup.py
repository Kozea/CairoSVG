#!/usr/bin/env python
#
# Public Domain

"""
CairoSVG - A Simple SVG Converter Based on Cairo
================================================

CairoSVG is a SVG converter based on Cairo. It can convert SVG files to PDF,
PostScript and PNG files.

For further information, please visit the `CairoSVG Website
<http://cairosvg.org/>`_.

"""

import re
import sys
from os import path

from setuptools import setup

init_path = path.join(path.dirname(__file__), 'cairosvg', '__init__.py')
with open(init_path, 'r', encoding='utf-8') as fd:
    version = re.search("__version__ = '([^']+)'", fd.read().strip()).group(1)

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

# When the version is updated, ``cairosvg.__version__`` must be modified.
# A new section in the ``NEWS`` file must be added too.
setup(
    name='CairoSVG',
    version=version,
    description='A Simple SVG Converter based on Cairo',
    long_description=__doc__,
    author='Kozea',
    author_email='guillaume.ayoub@kozea.fr',
    url='http://www.cairosvg.org/',
    license='GNU LGPL v3+',
    platforms='Any',
    packages=['cairosvg'],
    provides=['cairosvg'],
    setup_requires=pytest_runner,
    install_requires=['cairocffi', 'lxml', 'cssselect', 'pillow', 'tinycss'],
    tests_require=[
        'pytest-cov', 'pytest-flake8', 'pytest-isort', 'pytest-runner'],
    extras_require={'test': (
        'pytest-runner', 'pytest-cov', 'pytest-flake8', 'pytest-isort')},
    keywords=['svg', 'convert', 'cairo', 'pdf', 'png', 'postscript'],
    entry_points={'console_scripts': 'cairosvg=cairosvg:main'},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion'])

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

import sys

from setuptools import setup

if sys.version_info.major < 3:
    raise RuntimeError(
        'CairoSVG does not support Python 2.x anymore. '
        'Please use Python 3 or install an older version of CairoSVG.')

setup()

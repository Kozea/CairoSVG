# This file is part of CairoSVG
# Copyright © 2010-2015 Kozea
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with CairoSVG.  If not, see <http://www.gnu.org/licenses/>.

"""
CairoSVG - A simple SVG converter based on Cairo.

"""

__version__ = '2.1.3'  # noqa (version is used by relative imports)


import os
import sys
import argparse

from . import surface


SURFACES = {
    'PDF': surface.PDFSurface,
    'PNG': surface.PNGSurface,
    'PS': surface.PSSurface,
    'SVG': surface.SVGSurface,
}


def svg2svg(bytestring=None, *, file_obj=None, url=None, dpi=96,
            parent_width=None, parent_height=None, scale=1, unsafe=False,
            write_to=None):
    return surface.SVGSurface.convert(
        bytestring=bytestring, file_obj=file_obj, url=url, dpi=dpi,
        parent_width=parent_width, parent_height=parent_height, scale=scale,
        write_to=write_to)


def svg2png(bytestring=None, *, file_obj=None, url=None, dpi=96,
            parent_width=None, parent_height=None, scale=1, unsafe=False,
            write_to=None):
    return surface.PNGSurface.convert(
        bytestring=bytestring, file_obj=file_obj, url=url, dpi=dpi,
        parent_width=parent_width, parent_height=parent_height, scale=scale,
        write_to=write_to)


def svg2pdf(bytestring=None, *, file_obj=None, url=None, dpi=96,
            parent_width=None, parent_height=None, scale=1, unsafe=False,
            write_to=None):
    return surface.PDFSurface.convert(
        bytestring=bytestring, file_obj=file_obj, url=url, dpi=dpi,
        parent_width=parent_width, parent_height=parent_height, scale=scale,
        write_to=write_to)


def svg2ps(bytestring=None, *, file_obj=None, url=None, dpi=96,
           parent_width=None, parent_height=None, scale=1, unsafe=False,
           write_to=None):
    return surface.PSSurface.convert(
        bytestring=bytestring, file_obj=file_obj, url=url, dpi=dpi,
        parent_width=parent_width, parent_height=parent_height, scale=scale,
        write_to=write_to)


svg2svg.__doc__ = surface.Surface.convert.__doc__.replace(
    'the format for this class', 'SVG')
svg2png.__doc__ = surface.Surface.convert.__doc__.replace(
    'the format for this class', 'PNG')
svg2pdf.__doc__ = surface.Surface.convert.__doc__.replace(
    'the format for this class', 'PDF')
svg2ps.__doc__ = surface.Surface.convert.__doc__.replace(
    'the format for this class', 'PS')


def main():
    """Entry-point of the executable."""
    # Get command-line options
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('input', default='-', help='input filename or URL')
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '-f', '--format', help='output format',
        choices=sorted([surface.lower() for surface in SURFACES]))
    parser.add_argument(
        '-d', '--dpi', default=96, type=float,
        help='ratio between 1 inch and 1 pixel')
    parser.add_argument(
        '-W', '--width', default=None, type=float,
        help='width of the parent container in pixels')
    parser.add_argument(
        '-H', '--height', default=None, type=float,
        help='height of the parent container in pixels')
    parser.add_argument(
        '-s', '--scale', default=1, type=float, help='output scaling factor')
    parser.add_argument(
        '-u', '--unsafe', action='store_true',
        help='resolve XML entities and allow very large files '
             '(WARNING: vulnerable to XXE attacks and various DoS)')
    parser.add_argument('-o', '--output', default='-', help='output filename')

    options = parser.parse_args()
    kwargs = {
        'parent_width': options.width, 'parent_height': options.height,
        'dpi': options.dpi, 'scale': options.scale, 'unsafe': options.unsafe}
    kwargs['write_to'] = (
        sys.stdout.buffer if options.output == '-' else options.output)
    if options.input == '-':
        kwargs['file_obj'] = sys.stdin.buffer
    else:
        kwargs['url'] = options.input
    output_format = (
        options.format or
        os.path.splitext(options.output)[1].lstrip('.') or
        'pdf').upper()

    SURFACES[output_format.upper()].convert(**kwargs)

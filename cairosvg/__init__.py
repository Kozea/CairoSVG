# -*- coding: utf-8 -*-
# This file is part of CairoSVG
# Copyright © 2010-2012 Kozea
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
CairoSVG - A simple SVG converter for Cairo.

"""

import os
import sys
import optparse

from . import surface
from .surface import units


VERSION = "0.2"
SURFACES = {
    'SVG': surface.SVGSurface,  # Tell us if you actually use this one!
    'PNG': surface.PNGSurface,
    'PDF': surface.PDFSurface,
    'PS': surface.PSSurface}


# Generate the svg2* functions from SURFACES
for _output_format, _surface_type in SURFACES.items():
    _function = (
        # Two lambdas needed for the closure
        lambda surface_type: lambda *args, **kwargs:  # pylint: disable=W0108
        surface_type.convert(*args, **kwargs))(_surface_type)
    _name = 'svg2%s' % _output_format.lower()
    _function.__name__ = _name
    _function.__doc__ = surface.Surface.convert.__doc__.replace(
        'the format for this class', _output_format)
    setattr(sys.modules[__name__], _name, _function)


def main():
    """Entry-point of the executable."""
    # Get command-line options
    option_parser = optparse.OptionParser(
        usage="usage: %prog filename [options]", version=VERSION)
    option_parser.add_option(
        "-f", "--format", help="output format")
    option_parser.add_option(
        "-d", "--dpi", help="svg resolution")
    option_parser.add_option(
        "-o", "--output",
        default="", help="output filename")
    options, args = option_parser.parse_args()

    # Set the resolution
    if options.dpi:
        units.DPI = float(options.dpi)

    # Parse the SVG
    output_format = (
        options.format or
        os.path.splitext(options.output)[1].lstrip(".") or
        "pdf")

    # Print help if no argument is given
    if not args:
        option_parser.print_help()
        sys.exit()

    input_ = args[0]
    if input_ == "-":
        # Python 2/3 hack
        input_ = getattr(sys.stdin, "buffer", sys.stdin)

    if not options.output or options.output == '-':
        # Python 2/3 hack
        output = getattr(sys.stdout, "buffer", sys.stdout)
    else:
        output = options.output

    SURFACES[output_format.upper()].convert(file_obj=input_, write_to=output)

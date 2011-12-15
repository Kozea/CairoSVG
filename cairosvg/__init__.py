# -*- coding: utf-8 -*-
# This file is part of CairoSVG
# Copyright © 2010-2011 Kozea
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CairoSVG.  If not, see <http://www.gnu.org/licenses/>.

"""
CairoSVG - A simple SVG converter for Cairo.

"""

import os
import sys
import optparse

from . import parser, surface
from .surface import units


VERSION = "0.1.2"

SURFACES = {
    'png': surface.PNGSurface,
    'pdf': surface.PDFSurface,
    'ps': surface.PSSurface}


def main():
    """Entry-point of the executable."""
    # Get command-line options
    option_parser = optparse.OptionParser("usage: %prog filename [options]")
    option_parser.add_option(
        "-v", "--version", action="store_true",
        default=False, help="show version and exit")
    option_parser.add_option(
        "-f", "--format", help="output format")
    option_parser.add_option(
        "-d", "--dpi", help="svg resolution")
    option_parser.add_option(
        "-o", "--output",
        default="", help="output filename")
    options, args = option_parser.parse_args()

    # Print version and exit if the option is given
    if options.version:
        print(VERSION)
        sys.exit()

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
        try:
            input_ = sys.stdin.buffer  # Binary stream in Python 3
        except AttributeError:
            input_ = sys.stdin

    if not options.output or options.output == '-':
        try:
            output = sys.stdout.buffer  # Binary stream in Python 3
        except AttributeError:
            output = sys.stdout
    else:
        output = options.output

    content = SURFACES[output_format](input_, output).finish()

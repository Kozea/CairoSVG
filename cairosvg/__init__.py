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

from . import parser, surface_type, surface


VERSION = "0.1.2"


def svg2surface(svg, export_surface_type):
    """Return a ``surface`` corresponding to the ``svg`` string."""
    return export_surface_type(parser.Tree(svg))


def svg2pdf(svg):
    """Return a PDF string corresponding to the ``svg`` string."""
    return svg2surface(svg, surface_type.PDFSurface).read()


def svg2ps(svg):
    """Return a PostScript string corresponding to the ``svg`` string."""
    return svg2surface(svg, surface_type.PSSurface).read()


def svg2png(svg):
    """Return a PNG string corresponding to the ``svg`` string."""
    return svg2surface(svg, surface_type.PNGSurface).read()


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
        surface.DPI = float(options.dpi)

    # Parse the SVG
    output_format = (
        options.format or
        os.path.splitext(options.output)[1].lstrip(".") or
        "pdf")
    launcher = dict(pdf=svg2pdf, ps=svg2ps, png=svg2png)[output_format]

    # Print help if no argument is given
    if not args:
        option_parser.print_help()
        sys.exit()

    input_string = args[0]
    if input_string == "-":
        content = launcher(sys.stdin)
    else:
        content = launcher(input_string)

    if options.output:
        open(options.output, "w").write(content)
    else:
        print(content)

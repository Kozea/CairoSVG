#!/usr/bin/python
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
Cairo test suite.

This test suite compares the CairoSVG output with the reference output.

"""

import os
import cairosvg
import png

REFERENCE_FOLDER = os.path.join(os.path.dirname(__file__), "reference")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "output")
ALL_FILES = sorted((
        os.path.join(REFERENCE_FOLDER, filename)
        for filename in os.listdir(REFERENCE_FOLDER)
        if os.path.isfile(os.path.join(REFERENCE_FOLDER, filename))),
                   key=lambda name: name.lower())
FILES = (ALL_FILES[2 * i:2 * i + 2] for i in range(int(len(ALL_FILES) / 2)))
PIXEL_TOLERANCE = 65 * 255
SIZE_TOLERANCE = 1


if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)


def same(tuple1, tuple2, tolerence=0):
    """Return if the tuples values are quite the same."""
    for value1, value2 in zip(tuple1, tuple2):
        if abs(value1 - value2) > tolerence:
            return False
    return True


def generate_function(description):
    """Return a testing function with the given ``description``."""
    def check_image(png_filename, svg_filename):
        """Check that the pixels match between ``svg`` and ``png``."""
        width1, height1, pixels1, _ = png.Reader(png_filename).asRGBA()
        size1 = (width1, height1)
        png_filename = os.path.join(
            OUTPUT_FOLDER, os.path.basename(png_filename))
        with open(png_filename, "wb") as temp:
            filename = temp.name
            content = cairosvg.svg2png(svg_filename)
            temp.write(content)
        width2, height2, pixels2, _ = png.Reader(filename).asRGBA()
        size2 = (width2, height2)

        # Test size
        assert same(size1, size2, SIZE_TOLERANCE), \
            "Bad size (%s != %s)" % (size1, size2)

        # Test pixels
        width = min(width1, width2)
        height = min(height1, height2)
        pixels1 = list(pixels1)
        pixels2 = list(pixels2)
        # x and y are good variable names here
        # pylint: disable=C0103
        for x in range(width):
            for y in range(height):
                pixel_slice = slice(4 * x, 4 * (x + 1))
                pixel1 = list(pixels1[y][pixel_slice])
                alpha_pixel1 = (
                    [pixel1[3] * value for value in pixel1[:3]] +
                    [255 * pixel1[3]])
                pixel2 = list(pixels2[y][pixel_slice])
                alpha_pixel2 = (
                    [pixel2[3] * value for value in pixel2[:3]] +
                    [255 * pixel2[3]])
                assert same(alpha_pixel1, alpha_pixel2, PIXEL_TOLERANCE), \
                    "Bad pixel %i, %i (%s != %s)" % (x, y, pixel1, pixel2)
        # pylint: enable=C0103

    check_image.description = description
    return check_image


def test_images():
    """Yield the functions testing an image."""
    for png_filename, svg_filename in FILES:
        image_name = os.path.splitext(os.path.basename(png_filename))[0]
        yield (
            generate_function("Test the %s image" % image_name),
            png_filename, svg_filename)

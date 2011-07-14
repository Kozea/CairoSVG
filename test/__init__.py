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
import nose
from PIL import Image


REFERENCE_FOLDER = os.path.join(os.path.dirname(__file__), "reference")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "output")
ALL_FILES = sorted(
    os.path.join(REFERENCE_FOLDER, filename)
    for filename in os.listdir(REFERENCE_FOLDER))
FILES = (ALL_FILES[2*i:2*i+2] for i in range(len(ALL_FILES) / 2))
ALPHA_TOLERANCE_RATIO = 0.2 * 255
PIXEL_TOLERANCE = 15 * 255
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
    def check_image(png, svg):
        """Check that the pixels match between ``svg`` and ``png``."""
        image1 = Image.open(png)
        png_filename = os.path.join(OUTPUT_FOLDER, os.path.basename(png))
        with open(png_filename, "w") as temp:
            filename = temp.name
            content = cairosvg.svg2png(svg)
            temp.write(content)
        image2 = Image.open(filename)

        # Test size
        assert same(image1.size, image2.size, SIZE_TOLERANCE), \
            "Bad size (%s != %s)" % (image1.size, image2.size)

        # Test pixels
        width = min(image1.size[0], image2.size[0])
        height = min(image1.size[1], image2.size[1])
        for x in range(width):
            for y in range(height):
                pixel1, pixel2 = \
                    image1.getpixel((x, y)), image2.getpixel((x, y))
                alpha1, alpha2 = (
                    pixel1[3] if len(pixel1) == 4 else 1,
                    pixel2[3] if len(pixel2) == 4 else 1)
                alpha_pixel1 = [alpha1 * value for value in pixel1[:3]]
                alpha_pixel1 += [alpha1 * ALPHA_TOLERANCE_RATIO]
                alpha_pixel2 = [alpha2 * value for value in pixel2[:3]]
                alpha_pixel2 += [alpha2 * ALPHA_TOLERANCE_RATIO]
                assert same(alpha_pixel1, alpha_pixel2, PIXEL_TOLERANCE), \
                    "Bad pixel %i, %i (%s != %s)" % (x, y, pixel1, pixel2)

    check_image.description = description
    return check_image


def test_images():
    """Yield the functions testing an image."""
    for png, svg in FILES:
        image_name = os.path.splitext(os.path.basename(png))[0]
        yield generate_function("Test the %s image" % image_name), png, svg

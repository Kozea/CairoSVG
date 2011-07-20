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
import traceback
from PIL import Image


REFERENCE_FOLDER = os.path.join(os.path.dirname(__file__), "test", "reference")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "test", "output")
ALL_FILES = sorted(
    os.path.join(REFERENCE_FOLDER, filename)
    for filename in os.listdir(REFERENCE_FOLDER))
FILES = (ALL_FILES[2*i:2*i+2] for i in range(len(ALL_FILES) / 2))
PIXEL_TOLERANCE = 15 * 255
SIZE_TOLERANCE = 1


def same(tuple1, tuple2, tolerence=0):
    """Return if the tuples values are quite the same."""
    for value1, value2 in zip(tuple1, tuple2):
        if abs(value1 - value2) > tolerence:
            return False
    return True


if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)

for png, svg in FILES:
    print("Testing %s" % svg)
    image1 = Image.open(png)
    with open(os.path.join(OUTPUT_FOLDER, os.path.basename(png)), "w") as temp:
        filename = temp.name
        # Catch all exceptions, as we want the tests to continue
        # pylint: disable=W0702
        try:
            content = cairosvg.svg2png(svg)
        except:
            print("Error with this file")
            traceback.print_exc()
            os.remove(filename)
            continue
        else:
            temp.write(content)
        # pylint: enable=W0702
    image2 = Image.open(filename)

    # Test size
    if not same(image1.size, image2.size, SIZE_TOLERANCE):
        print("Bad size (%s != %s)" % (image1.size, image2.size))

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
            alpha_pixel2 = [alpha2 * value for value in pixel2[:3]]
            if not same(alpha_pixel1, alpha_pixel2, PIXEL_TOLERANCE):
                print("Bad pixel %i, %i (%s != %s)" % (x, y, pixel1, pixel2))
                break
        else:
            continue
        break
    else:
        print("OK")

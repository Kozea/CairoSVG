#!/usr/bin/python
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
Cairo test suite.

This test suite compares the CairoSVG output with the reference output.

"""

import os
import sys
import io
import tempfile
import shutil
import subprocess
from nose.tools import assert_raises, eq_  # pylint: disable=E0611

import cairo
import pystacia

from cairosvg import main
import cairosvg.parser
import cairosvg.surface


REFERENCE_FOLDER = os.path.join(os.path.dirname(__file__), "png")
TEST_FOLDER = os.path.join(os.path.dirname(__file__), "svg")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "output")

if os.environ.get("CAIROSVG_TEST_FILES"):
    ALL_FILES = os.environ["CAIROSVG_TEST_FILES"].split(",")
else:
    ALL_FILES = os.listdir(TEST_FOLDER)

ALL_FILES.sort(key=lambda name: name.lower())
FILES = [(
    os.path.join(
        os.path.dirname(REFERENCE_FOLDER) if name.startswith("fail")
        else REFERENCE_FOLDER, "%s.png" % os.path.splitext(name)[0]),
    os.path.join(
        os.path.dirname(TEST_FOLDER) if name.startswith("fail")
        else TEST_FOLDER, name))
    for name in ALL_FILES]
PIXEL_TOLERANCE = 65 * 255
SIZE_TOLERANCE = 1


if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)


def generate_function(description):
    """Return a testing function with the given ``description``."""
    if sys.version_info[0] >= 3:  # Python 3
        get_pixel = lambda pixels, i: list(pixels[i:i + 4])
    else:  # Python 2
        get_pixel = lambda pixels, i: map(ord, pixels[i:i + 4])

    def check_image(png_filename, svg_filename):
        """Check that the pixels match between ``svg`` and ``png``."""
        image1 = pystacia.read(png_filename).get_raw('RGBA')
        pixels1, width1, height1 = (
            image1['raw'], image1['width'], image1['height'])
        png_filename = os.path.join(
            OUTPUT_FOLDER, os.path.basename(png_filename))
        cairosvg.svg2png(url=svg_filename, write_to=png_filename, dpi=72)
        image2 = pystacia.read(png_filename).get_raw('RGBA')
        pixels2, width2, height2 = (
            image2['raw'], image2['width'], image2['height'])

        # Test size
        assert abs(width1 - width2) <= SIZE_TOLERANCE, \
            "Bad width (%s != %s)" % (width1, width2)
        assert abs(height1 - height2) <= SIZE_TOLERANCE, \
            "Bad height (%s != %s)" % (height1, height2)

        # Test pixels
        width = min(width1, width2)
        height = min(height1, height2)
        pixels1 = list(pixels1)
        pixels2 = list(pixels2)
        for i in range(0, 4 * width * height, 4):
            pixel1 = get_pixel(pixels1, i)
            alpha_pixel1 = (
                [pixel1[3] * value for value in pixel1[:3]] +
                [255 * pixel1[3]])
            pixel2 = get_pixel(pixels2, i)
            alpha_pixel2 = (
                [pixel2[3] * value for value in pixel2[:3]] +
                [255 * pixel2[3]])
            for value1, value2 in zip(alpha_pixel1, alpha_pixel2):
                assert abs(value1 - value2) <= PIXEL_TOLERANCE, \
                    "Bad pixel %i, %i (%s != %s)" % (
                        (i // 4) % width, (i // 4) // width, pixel1, pixel2)

    check_image.description = description
    return check_image


def test_images():
    """Yield the functions testing an image."""
    for png_filename, svg_filename in FILES:
        image_name = os.path.splitext(os.path.basename(png_filename))[0]
        yield (
            generate_function("Test the %s image" % image_name),
            png_filename, svg_filename)


MAGIC_NUMBERS = {
    'SVG': b'<?xml',
    'PNG': b'\211PNG\r\n\032\n',
    'PDF': b'%PDF',
    'PS': b'%!'}
SAMPLE_SVG = os.path.join(REFERENCE_FOLDER, 'arcs01.svg')


def test_formats():
    """Convert to a given format and test that output looks right."""
    _png_filename, svg_filename = FILES[0]
    for format_name in MAGIC_NUMBERS:
        # Use a default parameter value to bind to the current value,
        # not to the variabl as a closure would do.
        def test(format_name=format_name):
            """Test the generation of ``format_name`` images."""
            content = cairosvg.SURFACES[format_name].convert(url=svg_filename)
            assert content.startswith(MAGIC_NUMBERS[format_name])
        test.description = 'Test that the output from svg2%s looks like %s' % (
            format_name.lower(), format_name)
        yield test


def read_file(filename):
    """Shortcut to return the whole content of a file as a byte string."""
    with open(filename, 'rb') as file_object:
        return file_object.read()


def test_api():
    """Test the Python API with various parameters."""
    _png_filename, svg_filename = FILES[0]
    expected_content = cairosvg.svg2png(url=svg_filename)
    # Already tested above: just a sanity check:
    assert expected_content.startswith(MAGIC_NUMBERS['PNG'])

    svg_content = read_file(svg_filename)
    # Read from a byte string
    assert cairosvg.svg2png(svg_content) == expected_content
    assert cairosvg.svg2png(bytestring=svg_content) == expected_content

    with open(svg_filename, 'rb') as file_object:
        # Read from a real file object
        assert cairosvg.svg2png(file_obj=file_object) == expected_content

    file_like = io.BytesIO(svg_content)
    # Read from a file-like object
    assert cairosvg.svg2png(file_obj=file_like) == expected_content

    file_like = io.BytesIO()
    # Write to a file-like object
    cairosvg.svg2png(svg_content, write_to=file_like)
    assert file_like.getvalue() == expected_content

    temp = tempfile.mkdtemp()
    try:
        temp_1 = os.path.join(temp, 'result_1.png')
        with open(temp_1, 'wb') as file_object:
            # Write to a real file object
            cairosvg.svg2png(svg_content, write_to=file_object)
        assert read_file(temp_1) == expected_content

        temp_2 = os.path.join(temp, 'result_2.png')
        # Write to a filename
        cairosvg.svg2png(svg_content, write_to=temp_2)
        assert read_file(temp_2) == expected_content

    finally:
        shutil.rmtree(temp)

    file_like = io.BytesIO()
    assert_raises(TypeError, cairosvg.svg2png, write_to=file_like)


def test_low_level_api():
    """Test the low-level Python API with various parameters."""
    _png_filename, svg_filename = FILES[0]
    expected_content = cairosvg.svg2png(url=svg_filename)

    # Same as above, longer version
    tree = cairosvg.parser.Tree(url=svg_filename)
    file_like = io.BytesIO()
    surface = cairosvg.surface.PNGSurface(tree, file_like, 96)
    surface.finish()
    assert file_like.getvalue() == expected_content

    png_result = pystacia.read_blob(expected_content)
    expected_width, expected_height = png_result.size

    # Abstract surface
    surface = cairosvg.surface.PNGSurface(tree, None, 96)
    assert surface.width == expected_width
    assert surface.height == expected_height
    assert cairo.SurfacePattern(surface.cairo)
    assert_raises(Exception, cairo.SurfacePattern, 'Not a cairo.Surface.')


def test_script():
    """Test the ``cairosvg`` script and the ``main`` function."""
    _png_filename, svg_filename = FILES[0]
    script = os.path.join(os.path.dirname(__file__), '..', 'cairosvg.py')
    expected_png = cairosvg.svg2png(url=svg_filename)
    expected_pdf = cairosvg.svg2pdf(url=svg_filename)

    def run(*script_args, **kwargs):
        """Same as ``subprocess.check_output`` which is new in 2.7."""
        process = subprocess.Popen(
            [sys.executable, script] + list(script_args),
            stdout=subprocess.PIPE, **kwargs)
        output = process.communicate()[0]
        return_code = process.poll()
        assert return_code == 0
        return output

    def test_main(args, exit_=False, input_=None):
        """Test main called with given ``args``.

        If ``exit_`` is ``True``, check that ``SystemExit`` is raised. We then
        assume that the program output is an unicode string.

        If ``input_`` is given, use this stream as input stream.

        """
        sys.argv = ['cairosvg.py'] + args
        old_stdin, old_stdout = sys.stdin, sys.stdout

        output_buffer = io.BytesIO()
        if sys.version_info[0] >= 3:
            sys.stdout = io.TextIOWrapper(output_buffer)
        else:
            sys.stdout = output_buffer

        if input_:
            kwargs = {'stdin': open(input_, 'rb')}
            sys.stdin = open(input_, 'rb')
        else:
            kwargs = {}

        if exit_:
            try:
                main()
            except SystemExit:
                pass
            else:
                raise Exception('CairoSVG did not exit')
        else:
            main()

        sys.stdout.flush()
        output = output_buffer.getvalue()
        sys.stdin, sys.stdout = old_stdin, old_stdout
        eq_(output, run(*args, **kwargs))

        return output

    assert test_main([], exit_=True).startswith(b'Usage: ')
    assert test_main(['--help'], exit_=True).startswith(b'Usage: ')
    assert test_main(['--version'], exit_=True).strip() == \
         cairosvg.VERSION.encode('ascii')
    assert test_main([svg_filename]) == expected_pdf
    assert test_main([svg_filename, '-d', '72', '-f', 'Pdf']) == expected_pdf
    assert test_main([svg_filename, '-f', 'png']) == expected_png
    assert test_main(['-'], input_=svg_filename) == expected_pdf

    # Test DPI
    output = test_main([svg_filename, '-d', '10', '-f', 'png'])
    width, height = pystacia.read_blob(output).size
    eq_(width, 47)
    eq_(height, 20)

    temp = tempfile.mkdtemp()
    try:
        temp_1 = os.path.join(temp, 'result_1')
        # Default to PDF
        assert not test_main([svg_filename, '-o', temp_1])
        assert read_file(temp_1) == expected_pdf

        temp_2 = os.path.join(temp, 'result_2.png')
        # Guess from the file extension
        assert not test_main([svg_filename, '-o', temp_2])
        assert read_file(temp_2) == expected_png

        temp_3 = os.path.join(temp, 'result_3.png')
        # Explicit -f wins
        assert not test_main([svg_filename, '-o', temp_3, '-f', 'pdf'])
        assert read_file(temp_3) == expected_pdf
    finally:
        shutil.rmtree(temp)

"""
CairoSVG non-regression tests.

This test suite compares the CairoSVG output with a reference version
output.

"""

import os
import tempfile

import pytest

from . import FILES, cairosvg, reference_cairosvg


@pytest.mark.parametrize('svg_filename', FILES)
def test_image(svg_filename):
    """Check that the pixels match between ``svg`` and ``png``."""
    test_png = tempfile.NamedTemporaryFile(
        prefix='test-', suffix='.png', delete=False)
    test_surface = cairosvg.surface.PNGSurface(
        cairosvg.parser.Tree(url=svg_filename, unsafe=True), test_png,
        dpi=72)
    test_pixels = test_surface.cairo.get_data()[:]

    ref_png = tempfile.NamedTemporaryFile(
        prefix='reference-', suffix='.png', delete=False)
    ref_surface = reference_cairosvg.surface.PNGSurface(
        reference_cairosvg.parser.Tree(url=svg_filename, unsafe=True),
        ref_png, dpi=72)
    ref_pixels = ref_surface.cairo.get_data()[:]

    if test_pixels == ref_pixels:
        # Test is passing
        os.remove(ref_png.name)
        os.remove(test_png.name)
    else:  # pragma: no cover
        ref_surface.finish()
        test_surface.finish()

        raise AssertionError(
            'Images are different: {} {}'.format(
                ref_png.name, test_png.name))


def test_image_with_relative_path():
    test_image('./struct-image-01-t.svg')

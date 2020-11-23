"""
CairoSVG helpers tests.

"""

from . import cairosvg

helpers = cairosvg.helpers


def test_distance():
    """Test ``helpers.distance``."""
    helpers.distance(0, 0, 0, 10) == 10
    helpers.distance(10, 20, 10, 20) == 0
    helpers.distance(-10, -1.5, 10, -1.5) == 20


def test_normalize():
    """Test ``helpers.normalize``."""
    helpers.normalize('') == ''
    helpers.normalize('1') == '1'
    helpers.normalize('1.1 2') == '1.1 2'
    helpers.normalize('1.1,2 3,4.') == '1.1 2 3 4.'
    helpers.normalize('1.1,2.3.2') == '1.1 2.3 .2'
    helpers.normalize('1.1,2.3.2.4') == '1.1 2.3 .2 .4'
    helpers.normalize('1.1,2.3.2-.4') == '1.1 2.3 .2 -.4'
    helpers.normalize('\t-1\n   ,2.3  ') == '-1 2.3'
    helpers.normalize('1,2,3,4') == '1 2 3 4'
    helpers.normalize('-12.e3  13E-8.1,') == '-12.e3 13e-8.1'
    helpers.normalize('.1.2-.2e3.2.13E-8.1.1\n') == (
        '.1 .2 -.2e3.2 .13e-8.1 .1')

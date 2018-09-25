# This file is part of CairoSVG
# Copyright © 2010-2018 Kozea
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

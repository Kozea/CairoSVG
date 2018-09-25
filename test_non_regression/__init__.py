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
Cairo test suite.

"""

import os
import imp

import cairosvg


reference_cairosvg = imp.load_source(
    'cairosvg_reference', pathname=os.path.join(
        os.path.dirname(__file__), 'cairosvg_reference', 'cairosvg',
        '__init__.py'))

cairosvg.features.LOCALE = reference_cairosvg.features.LOCALE = 'en_US'

TEST_FOLDER = os.path.join(os.path.dirname(__file__), 'svg')

os.chdir(TEST_FOLDER)  # relative image urls

if os.environ.get('CAIROSVG_TEST_FILES'):  # pragma: no cover
    ALL_FILES = os.environ['CAIROSVG_TEST_FILES'].split(',')
else:
    ALL_FILES = os.listdir(TEST_FOLDER)

ALL_FILES.sort(key=lambda name: name.lower())
FILES = [
    os.path.join(
        os.path.dirname(TEST_FOLDER) if name.startswith('fail')
        else TEST_FOLDER, name)
    for name in ALL_FILES]

"""
Cairo test suite.

"""

import imp
import os

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

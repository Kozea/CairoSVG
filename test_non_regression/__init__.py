"""
Cairo test suite.

"""

import importlib.util
import os
import sys
from pathlib import Path

import cairosvg

CURRENT_FOLDER = Path(__file__).parent
TEST_FOLDER = CURRENT_FOLDER / 'svg'

reference_spec = importlib.util.spec_from_file_location(
    'cairosvg_reference',
    CURRENT_FOLDER / 'cairosvg_reference' / 'cairosvg' / '__init__.py')
reference_cairosvg = importlib.util.module_from_spec(reference_spec)
sys.modules['cairosvg_reference'] = reference_cairosvg
reference_spec.loader.exec_module(reference_cairosvg)

cairosvg.features.LOCALE = reference_cairosvg.features.LOCALE = 'en_US'
os.chdir(TEST_FOLDER)  # relative image urls

if os.environ.get('CAIROSVG_TEST_FILES'):  # pragma: no cover
    FILES = [
        str(CURRENT_FOLDER / filename) for filename in
        os.environ['CAIROSVG_TEST_FILES'].split(',')]
else:
    FILES = [str(path) for path in TEST_FOLDER.iterdir()]
FILES.sort(key=lambda path: path.lower())

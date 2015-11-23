=======
 Tests
=======

The CairoSVG testing suite is based on the official SVG test suite available on
the W3 website:

http://www.w3.org/Graphics/SVG/WG/wiki/Test_Suite_Overview

You'll find in this folder:

- ``*.py`` with various tests inside
- ``svg`` with the source SVG files for non-regression tests
- ``resources`` and ``images`` with various resources for the SVG files
- ``fail`` with the failing tests

Most of the tests are regression tests: they generate reference images using an
old version on CairoSVG and compare them to the current version. These tests
are really useful if you changed the code.

If you want to check that CairoSVG works on your computer, you should launch
tests in ``cairosvg/test_api.py``.

You can test CairoSVG by launching ``nosetests`` or ``py.test`` in the root
folder of the repository. You can launch the tests only on one image (or more
than one, separated by a comma) using::

  CAIROSVG_TEST_FILES=image.svg nosetests --match=test_images test/test_non_regression.py

As CairoSVG does not handle SVG fonts, you can install the corresponding OTF
fonts in order to test CairoSVG with the right fonts. They have already been
generated for you in the ``resources`` folder.

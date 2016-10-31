=======
 Tests
=======

You'll find in this folder:

- ``*.py`` with various tests inside
- ``svg`` with the source SVG files for non-regression tests
- ``resources`` and ``images`` with various resources for the SVG files
- ``fail`` with the failing tests

If you want to check that CairoSVG works on your computer, you should not
launch the tests here, you should instead launch tests in
``cairosvg/test_api.py``::

  pytest cairosvg/test_api.py

The tests here are regression tests: they generate reference images using an
old version on CairoSVG and compare them to the current version. They are based
on the official SVG test suite available on the W3 website:

http://www.w3.org/Graphics/SVG/WG/wiki/Test_Suite_Overview

These tests are really useful if you changed the code. You can launch both
these tests and the API tests by getting the submodule and launching
``./setup.py test`` in the root folder of the repository::

  git submodule update --init
  ./setup.py test

You can launch the tests only on one image (or more than one, separated by a
comma) using::

  env CAIROSVG_TEST_FILES=image.svg pytest test/test_non_regression.py

As CairoSVG does not handle SVG fonts, you can install the corresponding OTF
fonts in order to test CairoSVG with the right fonts. They have already been
generated for you in the ``resources`` folder.

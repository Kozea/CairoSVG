=======
 Tests
=======

The CairoSVG testing suite is based on the official SVG test suite available on
the W3 website:

http://www.w3.org/Graphics/SVG/WG/wiki/Test_Suite_Overview

You'll find in this folder:

- ``svg`` with the source SVG files
- ``png`` with the reference PNG files
- ``resources`` and ``images`` with various resources for the SVG files
- ``fail`` with the failing tests
- ``output`` with the test output PNG files

You can test CairoSVG by launching ``nosetests`` in the root folder of the
repository. You can launch the tests only on one image (or more than one,
separated by a comma) using::

  CAIROSVG_TEST_FILES=image.svg nosetests --match=test_images test

As CairoSVG does not handle SVG fonts, you can generate OTF fonts and install
them in order to test CairoSVG with the right fonts. They have already been
generated for you in the ``resources`` folder. There's also a script called
``generate.py`` in the ``resources`` folder that can do that again if you have
FontForge installed on your system.

The version of cairo needed to make these tests work perfectly is 1.12.8.

You need these fonts to be installed to get pixel-by-pixel equivalent images in
the tests:

- Anglepoise
- Blocky
- CalaLig
- SVGFreeSans
- Liberation Sans
- FreeSerifBoldItalic

You also need Arial to be aliased by Liberation Sans (may already be done by
your distribution).

Last but not least, you have to install ``tinycss``, ``cssselect``, ``lxml``
and ``pystacia`` to make the CSS- and raster-related tests pass correctly.

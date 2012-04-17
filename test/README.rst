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
repository.

As CairoSVG does not handle SVG fonts, you can generate OTF fonts and install
them in order to test CairoSVG with the right fonts. They have already been
generated for you in the ``resources`` folder. There's also a script called
``generate.py`` in the ``resources`` folder that can do that again if you have
FontForge installed on your system.

You need these fonts to be installed to get pixel-by-pixel equivalent images in
the tests:

- Blocky
- CalaLig
- SVGFreeSans
- Liberation Sans

You also need Arial to be aliased by Liberation Sans (may already be done by
your distribution).

Last but not least, you have to install ``tinycss`` to make the CSS-related
tests pass correctly.

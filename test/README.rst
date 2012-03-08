=======
 Tests
=======

The CairoSVG testing suite is based on the official SVG test suite available on
the W3 website:

`http://www.w3.org/Graphics/SVG/WG/wiki/Test_Suite_Overview`_

You'll find in this folder:

- ``svg`` with the source SVG files
- ``png`` with the reference PNG files
- ``resources`` and ``images`` with various resources for the SVG files
- ``fail`` with the failing tests
- ``output`` with the test output PNG files

You can test CairoSVG by launching ``nosetests`` in the root folder of the
repository.

====================
 User Documentation
====================

:Author: Guillaume Ayoub

:Date: 2011-02-13

:Abstract: This document is a short description for installing and using
 CairoSVG.

.. editable::

.. contents::

Installation
============

Dependencies
------------

CairoSVG is written in pure Python and only depends on `Pycairo
<http://cairographics.org/pycairo/>`_ or `cairocffi
<https://github.com/SimonSapin/cairocffi>`_. It is known to work with
Python 2.6, 2.7, 3.2 and 3.3.

Linux and OS X users certainly have Python already installed. For Windows
users, please install `Python <http://python.org/download/>`_ thanks to the
adequate installer.

CairoSVG can use `lxml <http://lxml.de/>`_ to parse the SVG file, and `tinycss
<http://packages.python.org/tinycss/>`_ plus `cssselect
<http://packages.python.org/cssselect/>`_ to apply CSS not included in the
``style`` attribute of the tags. If these packages are not available, CSS will
only be supported in the ``style`` attributes.

Embedded raster images other than PNG are handled by `Pillow
<http://python-imaging.github.io/>`_.


CairoSVG
--------

CairoSVG can be freely downloaded on the `project website, download section
<http://www.cairosvg.org/download>`_. Just get the file and unzip it in a
folder of your choice.


Command-Line Usage
==================

Description
-----------

Here is the simple CairoSVG usage::

  Usage: cairosvg.py filename [options]

  Options:
    -h, --help            show this help message and exit
    -v, --version         show version and exit
    -f FORMAT, --format=FORMAT
                          output format
    -d DPI, --dpi=DPI     ratio between 1in and 1px
    -o OUTPUT, --output=OUTPUT
                          output filename

Supported output formats are ``pdf``, ``ps`` and ``png`` (default is
``pdf``). The default output is the standard output. If an output filename is
given, the format is automatically chosen according to the extension.

The ``dpi`` options sets the ratio between pixels and real-life units such
as millimeters and inches (as explained in the `specification
<http://www.w3.org/TR/SVG11/coords.html>`_).

Moreover, if ``-`` is used as filename, CairoSVG reads the SVG string from the
standard input.

Examples
--------

Here are some usage examples:

.. code-block:: bash

  # Convert to pdf, write to standard output
  cairosvg test.svg

  # Convert to png, write to standard output
  cairosvg test.svg -f png

  # Convert to ps, write to test.ps
  cairosvg test.svg -o test.ps

  # Convert an SVG string to pdf, write to standard output
  echo "<svg height='30' width='30'><text y='10'>123</text></svg>" \
       | cairosvg -


API
===

The ``cairosvg`` module offers 4 functions:

- ``svg2pdf``,
- ``svg2png``,
- ``svg2ps``, and
- ``svg2svg`` (!).

These functions expect *one* of these parameters:

- ``bytestring``, a byte string containing SVG, or
- ``url``, an URL or a filename, or
- ``file_obj``, a file-like object.

If the ``write_to`` argument is provided (filename or file-like object), the
output is written there. Otherwise, the function returns a byte string.

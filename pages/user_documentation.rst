====================
 User Documentation
====================

:Author: Guillaume Ayoub

:Date: 2011-02-13

:Abstract: This document is a short description for installing and using
 CairoSVG.

.. contents::

Installation
============

Dependencies
------------

CairoSVG is written in pure python and only depends on Pycairo [#]_. It is
known to work on Python 2.6 and 2.7.

Linux users certainly have Python already installed. For Windows and MacOS
users, please install Python [#]_ thanks to the adequate installer.

.. [#] `Pycairo website <http://cairographics.org/pycairo/>`_.

.. [#] `Python download page <http://python.org/download/>`_.

CairoSVG
--------

CairoSVG can be freely downloaded on the `project website, download section
<http://www.cairosvg.org/download>`_. Just get the file and unzip it in a
folder of your choice.


Usage
=====

Description
-----------

Here is the simple CairoSVG usage::

  Usage: cairosvg filename [options]

  Options:
    -h, --help            show this help message and exit
    -v, --version         show version and exit
    -f FORMAT, --format=FORMAT
                          output format
    -o OUTPUT, --output=OUTPUT
                          output filename

Supported output formats are ``pdf``, ``ps`` and ``png`` (default is
``pdf``). The default output is the standard output. If an output filename is
given, the format is automatically chosen according to the extension.

Moreover, you can directly use an SVG string instead of ``filename``.

Examples
--------

Here are some usage examples::

  # Convert to pdf, write to standard output
  cairosvg test.svg

  # Convert to png, write to standard output
  cairosvg test.svg -f png

  # Convert to ps, write to test.ps
  cairosvg test.svg -o test.ps

  # Convert an SVG string to pdf, write to standard output
  cairosvg "<svg height='30' width='30'><text y='10'>123</text></svg>"

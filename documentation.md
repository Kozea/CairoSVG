---
layout: page
title: Documentation
permalink: /documentation
---

## What is CairoSVG?

CairoSVG is a **[SVG 1.1](http://www.w3.org/TR/SVG/) to PNG, PDF, PS** and
SVG converter. It provides both a **command-line interface** and **Python
3.4+** library, for Unix-like operating systems (at least **Linux** and
**OS X**) and **Windows**. It is a free software, distributed under **LGPLv3**.

CairoSVG is written in Python and based on the famous 2D graphics library
called [Cairo](http://cairographics.org/). It is tested on SVG samples coming
from the
[W3C test suite](http://www.w3.org/Graphics/SVG/WG/wiki/Test_Suite_Overview). It
also relies on [lxml](http://lxml.de/) to parse the SVG file, and
[tinycss](http://packages.python.org/tinycss/) plus
[cssselect](http://packages.python.org/cssselect/) to apply CSS. Embedded
raster images are handled by [Pillow](http://python-imaging.github.io/).


## How to use CairoSVG?

### Command line

Here is the simple CairoSVG command line usage:

    $ cairosvg --help
    usage: cairosvg.py [-h] [-v] [-f {pdf,png,ps,svg}] [-d DPI] [-o OUTPUT] input

    CairoSVG - A simple SVG converter based on Cairo.

    positional arguments:
      input                 input filename or URL

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -f {pdf,png,ps,svg}, --format {pdf,png,ps,svg}
                            output format
      -d DPI, --dpi DPI     ratio between 1in and 1px
      -o OUTPUT, --output OUTPUT
                            output filename

Supported output formats are `pdf`, `ps`, `png` and `svg` (default is
`pdf`). The default output is the standard output. If an output filename is
given, the format is automatically chosen according to the extension.

The `dpi` options sets the ratio between pixels and real-life units such as
millimeters and inches (as explained in the
[specification](http://www.w3.org/TR/SVG11/coords.html)).

Moreover, if ``-`` is used as filename, CairoSVG reads the SVG string from the
standard input.

### Python

CairoSVG provides a module for Python 3.4+.

The `cairosvg` module offers 4 functions:

- `svg2pdf`,
- `svg2png`,
- `svg2ps`, and
- `svg2svg`.

These functions expect one of these parameters:

- `bytestring`, a byte string containing SVG, or
- `url`, an URL or a filename, or
- `file_obj`, a file-like object.

If the `write_to` argument is provided (filename or file-like object), the
output is written there. Otherwise, the function returns a byte string.


## How good is CairoSVG at following the specification?

CairoSVG is generally good at supporting the widely used features of
SVG. You'll find a full list of supported features on
[the SVG 1.1 support page](/svg_support).

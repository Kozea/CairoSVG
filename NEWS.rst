======
 News
======


Version 2.8.2 released on 2025-05-15
====================================

* Allow both Unicode strings and bytes as input


Version 2.8.1 released on 2025-05-14
====================================

* Allow both text- and bytes-based file objects as input


Version 2.8.0 released on 2025-05-12
====================================

* Drop support of Python 3.7 and 3.8, add support of Python 3.12 and 3.13
* Optimize math operations
* Use pathlib
* Close paths for ellipses and circles
* Fix output ratio for SVG surfaces
* Avoid endless loops when updating def attributes
* Round PNG size
* Don’t crash when more than 2 values are given to translate and scale functions


Version 2.7.1 released on 2023-08-05
====================================

* Don’t draw clipPath when defined after reference
* Handle evenodd fill rule with gradients and patterns
* Fix ratio and clip for "image" tags with no size
* Handle data-URLs in safe mode
* Use f-strings


Version 2.7.0 released on 2023-03-20
====================================

**WARNING:** this is a security update.

When processing SVG files, CairoSVG could access other files online, possibly
leading to very long renderings or other security problems.

This feature is now disabled by default. External resources can still be
accessed using the "unsafe" or the "url_fetcher" parameter.


Version 2.6.0 released on 2023-01-12
====================================

* Drop support of Python 3.5 and 3.6, add support of Python 3.9, 3.10 and 3.11
* Support crispEdges value for text antialiasing
* Don’t crash when including CMYK images
* Only update docstrings when not optimized
* Don’t restore current point after empty paths
* Assume that 1ch equals 0.5em
* Fix various deprecation warnings


Version 2.5.2 released on 2021-03-06
====================================

* Fix marker path scale


Version 2.5.1 released on 2021-01-06
====================================

**WARNING:** this is a security update.

When processing SVG files, CairoSVG was using two regular expressions which are
vulnerable to Regular Expression Denial of Service (REDoS).

If an attacker provided a malicious SVG, it could make CairoSVG get stuck
processing the file for a very long time.

Other bug fixes:

* Fix marker positions for unclosed paths
* Follow hint when only output_width or output_height is set
* Handle opacity on raster images
* Don’t crash when use tags reference unknown tags
* Take care of the next letter when A/a is replaced by l
* Fix misalignment in node.vertices


Version 2.5.0 released on 2020-10-29
====================================

* Drop support of Python 3.5, add support of Python 3.9.
* Add EPS export
* Add background-color, negate-colors, and invert-images options
* Improve support for font weights
* Fix opacity of patterns and gradients
* Support auto-start-reverse value for orient
* Draw images contained in defs
* Add Exif transposition support
* Handle dominant-baseline
* Support transform-origin


Version 2.4.2 released on 2019-09-10
====================================

* Fix race condition in tests
* Fix scale for images with no viewBox


Version 2.4.1 released on 2019-08-21
====================================

* Fix the --scale parameter
* Allow href attributes with no namespace
* Fix the tree root detection


Version 2.4.0 released on 2019-05-20
====================================

* Fix aspect and position when resizing root SVG tag
* Follow aspect and position hints when using forced output size


Version 2.3.1 released on 2019-04-18
====================================

* Fix relative paths on Windows


Version 2.3.0 released on 2019-02-08
====================================

* Drop Python 3.4 support
* Make text selectable on generated PDF files
* Don't inherit dx and dy attributes
* Fix support of alignment-baseline="hanging"
* Fix backslashes in docstrings and comments
* Fix local anchors with files with no given URL
* Close VERSION's file descriptor
* Clean packaging
* Include LICENSE in distributed packages


Version 2.2.1 released on 2018-09-27
====================================

* Fix packaging


Version 2.2.0 released on 2018-09-21
====================================

* Clean packaging
* Fix T commands used with previous relative commands in paths
* Use real functions for svg2* commands, improving IDE integration
* Fix files management on Windows
* Handle image-rendering property
* Fix crash with some text samples
* Fix position of embedded svg tags with a viewbox not at position (0, 0)
* Add output-width and output-height options
* Handle references to inner document tags defined after the anchor
* Fix offsets for texts on paths


Version 2.1.3 released on 2018-01-03
====================================

* Fix T commands following q or t in paths


Version 2.1.2 released on 2017-12-01
====================================

* Fix font-size


Version 2.1.1 released on 2017-09-30
====================================

* Use http://www.w3.org/2000/svg as default namespace


Version 2.1.0 released on 2017-09-30
====================================

* Use cssselect2 and tinycss2 instead of cssselect and tinycss
* Don't require lxml anymore
* Rely on defusedxml to detect unsafe SVG files


Version 2.0.3 released on 2017-05-02
====================================

* Add ``python_requires`` in ``setup.py``


Version 2.0.2 released on 2017-03-20
====================================

* Handle ``text-align`` in textPath tags
* Test with Python 3.6


Version 2.0.1, released on 2017-01-04
=====================================

* Don't crash on relative refs with no input URL


Version 2.0.0, released on 2016-11-24
=====================================

* Drop Python 2 support
* Drop pycairo support
* Rely on cairocffi, lxml, cssselect, pillow and tinycss
* Fix markers
* Fix URL/id handling
* Use bounding boxes for gradients
* Split deployment and development tests
* Add a scale option
* Add a parent size option
* Test with Travis


Version 1.0.22, released on 2016-06-16
======================================

* Fix crash when lxml is not installed


Version 1.0.21, released on 2016-06-14
======================================

**WARNING:** this is a security update.

CairoSVG was vulnerable to XML eXternal Entity (XXE) attacks, this release
fixes this vulnerability by not resolving the XML entities anymore.

The ``--unsafe`` option has been added to force the resolution of XML
entities. Obviously, this option is not safe and should only be used with
trusted SVG files.


Version 1.0.20, released on 2016-02-23
======================================

* Allow the user to give parent size


Version 1.0.19, released on 2015-10-30
======================================

* Drastically improve the performance of ``Node()``


Version 1.0.18, released on 2015-10-20
======================================

* Use cairo groups to apply filters


Version 1.0.17, released on 2015-10-09
======================================

* Fix scale and position of markers


Version 1.0.16, released on 2015-08-05
======================================

* Support the text-rendering property


Version 1.0.15, released on 2015-06-22
======================================

* Use xMidYMid as default preserveAspectRatio value


Version 1.0.14, released on 2015-06-02
======================================

* Support the shape-rendering property


Version 1.0.13, released on 2015-02-26
======================================

* Fix end markers


Version 1.0.12, released on 2015-02-26
======================================

* Don't crash when paths with markers end with a move_to action


Version 1.0.11, released on 2015-02-11
======================================

* Allow commas in viewboxes


Version 1.0.10, released on 2015-02-09
======================================

* Allow quotes around font names


Version 1.0.9, released on 2014-08-12
=====================================

* Don't crash when gradients are applied to paths


Version 1.0.8, released on 2014-07-14
=====================================

* Don't create an atomic layer for transparent tags with no children


Version 1.0.7, released on 2014-05-06
=====================================

* Fix scaling with negative viewBox origin
* Automatically detect size and position of circles and ellipses for gradients


Version 1.0.6, released on 2014-03-07
=====================================

* Fall back to pycairo if cairocffi is unable to find the cairo library


Version 1.0.5, released on 2014-03-06
=====================================

* Don't inherit clip* and overflow properties
* Don't transform the root svg tag according to the PreservAspectRatio attribute
* Add simple support for alignment-baseline
* Add cairocffi into setup.py deps


Version 1.0.4, released on 2014-01-21
=====================================

* Clear relative coordinates when absolute coordinates are set in tspan tags


Version 1.0.3, released on 2013-11-27
=====================================

* Fix clips and viewboxes
* Don't draw an empty image when locale is not set


Version 1.0.2, released on 2013-11-19
=====================================

* Don't crash when locale is not set
* Get the xml_tree from the root parent when creating nodes from string


Version 1.0.1, released on 2013-09-24
=====================================

* Don't crash when svg tag has no width or height


Version 1.0, released on 2013-09-06
===================================

* CairoCFFI support
* Support of more external CSS stylesheets
* Handle more filters
* Use pillow instead of pystacia
* Fix a lot of bugs with text (whitespaces, text on a path, etc.)
* Inherit attributes in ``use`` tags
* Cache trees for ``use`` tags
* Handle conditional structures


Version 0.5, released on 2012-12-13
===================================

* Simple support of the ``image`` tag thanks to pystacia
* Better tests with pystacia instead of pypng (~35% faster)
* Handle s after C/S and S after c/s in paths
* Handle rounded corners with 2 different radii for rectangles
* Fix python 2.6 support
* Fix markers with empty paths and z/Z points
* Fix initial m in paths with no current point
* Fix transformations order


Version 0.4.4, released on 2012-07-05
=====================================

* Use a default font size of 12pt
* Fix a bug about non-invertible matrices
* Fix the installation for python 3 with LANG=C


Version 0.4.3, released on 2012-05-04
=====================================

* Fix the version detection without cairo


Version 0.4.2, released on 2012-05-04
=====================================

* Don't rely on cairo import to find the version


Version 0.4.1, released on 2012-04-25
=====================================

* Use cssselect


Version 0.4, released on 2012-04-19
===================================

* Reliable testing suite
* Use tinycss instead of cssutils to parse CSS


Version 0.3.1, released on 2012-02-20
=====================================

* Percentages, em and ex units
* Real opacity


Version 0.3, released on 2012-01-27
===================================

* Simple inline CSS support
* Support for transformations in patterns and gradients
* Real by-surface DPI management (default value set to 96)
* Handle exponents


Version 0.2, released on 2012-01-04
===================================

* **Change the Python API again** to be compatible with 0.1.1 and before:
  ``svg2pdf(source_as_bytes) -> bytes`` but still support filenames or
  file objects with keyword-only parameters. See the docstrings.
* Add support for ``display``, ``visibility``, ``stop-opacity`` and
  ``stroke-miterlimit``
* Internal refactoring


Version 0.1.2, released on 2011-12-14
=====================================

**Backward incompatible change** in the Python API: previously the input
could be either a filename or SVG content as a string. Now a string is always
interpreted as a filename, but file-like objects are also accepted.
Use a StringIO object if you have SVG content in a string.


Version 0.1.1, released on 2011-12-13
=====================================

Fix Python 2.6 compatibility.


Version 0.1, released on 2011-12-13
===================================

* First release
* PDF, PS and PNG export
* Easy installer

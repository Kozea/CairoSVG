======
 News
======


Version 2.0, not released yet
=============================

* Fix markers
* Fix URL/id handling


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

======
 News
======


Version 1.0, not released yet
=============================

* Better tests (~5% faster)
* Fix python 2.6 support
* Fix markers with empty paths and z/Z points


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

======
 News
======

Version 0.2, released on 2011-12-XX
===================================

* **Break the Python API again**. Use
  ``cairosvg.surface.PDFSurface(input, output).finish()``.
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

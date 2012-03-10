=====
 Use
=====

Circular Dependencies
=====================

- ``struct-use-08-b``
- ``struct-use-12-b``

These tests fail because some of the ``use`` tags they include create circular
dependencies.

The way to handle circular dependancies in not really clear in the
specification. You can find some information in the `specification of the use
tag <http://www.w3.org/TR/SVG/struct.html#UseElement>`_, where it's said to be
an error. If this error doesn't have to be handled according to the
specification, then this test can safely fail.


Use Attributes
==============

- other ``struct-use-*``

Used elements must inherit the attributes of the original document they're
coming from, and they must inherit the attributes of the ``use`` tag in the
destination document. That's why we have to parse the full SVG document of the
external used element, and then include the node referenced in the ``use`` tag
as a child of the ``use`` tag.

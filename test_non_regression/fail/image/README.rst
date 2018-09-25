=======
 Image
=======

Gamma
=====

- ``struct-image-03-t``

This test fails because the image drawn by the PIL don't respect the gAMA
chunk included in PNG files. We don't really care.


Circular Dependencies and Root of URLs
======================================

- ``struct-image-12-b``

This test fails because of the same 2 first reasons given in the ``use``
folder:

- an image referencing itself, leading to an infinite loop; and
- the referenced URLs not being given a root URL corresponding to the current
  SVG file path.

Fixing the tests referenced in the ``use`` floder would definitely help fixing
this test.

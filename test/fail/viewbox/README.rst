=========
 ViewBox
=========

No Size
=======

- ``struct-frag-01-t``
- ``struct-frag-04-t``

These tests fail because there's no viewbox and no size set for the root
``svg`` tag. In this case, the SVG agent has to use the parent size, which is
meaningless for CairoSVG.

CairoSVG could get the bounding boxes of the children and try to get a kind of
*minimal size* to create its Cairo surface, but that's not the easiest thing to
code. Anyway, that's not a really important bug, as SVG files generally have a
root viewbox set.


Bad Viewbox
===========

- ``coords-viewattr-03-b``

The nested ``svg`` tags mean something different for CairoSVG, at least for
multi-page formats: one non-root ``svg`` is another page, and the ``viewbox``
is then something special. The PNG output should handle correctly the
``viewbox`` attribute.

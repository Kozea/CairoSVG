=========
 ViewBox
=========

No Size, Empty ViewBox
======================

- ``struct-frag-*``

These tests fail because there's no viewbox (or an empty one) and no size set
for the root ``svg`` tag. In this case, the SVG agent has to use the parent
size, which is meaningless for CairoSVG.

CairoSVG could get the bounding boxes of the children and try to get a kind of
*minimal size* to create its Cairo surface, but that's not the easiest thing to
code. Anyway, that's not a really important bug, as SVG files generally have a
root viewbox set.


Bad Viewbox and Nested ``svg`` Tags
===================================

- ``coords-viewattr-03-b``
- ``masking-path-03-b``
- ``masking-path-14-f``
- ``struct-svg-03-f``
- ``struct-group-02-b``

The nested ``svg`` tags mean something different for CairoSVG, at least for
multi-page formats: one non-root ``svg`` is another page, and the ``viewbox``
is then something special. The PNG output should handle correctly the
``viewbox`` attribute.

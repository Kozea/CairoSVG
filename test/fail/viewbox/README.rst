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

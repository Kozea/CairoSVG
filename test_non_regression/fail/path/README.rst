======
 Path
======

Bevel Shape
===========

- ``paths-data-18-f``

This text fails because the bevel shape is different in Cairo and in the SVG
specification.

Cairo
  "the join is cut off at half the line width from the joint point"
SVG Specification
  according to the drawing, the join is cut off at
  (line width * (1 - cos(theta / 2))) from the join point

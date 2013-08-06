======
 Mask
======

Luminance Masks
===============

- ``masking-intro-01-f``
- ``masking-path-11-b``

SVG relies on the luminance and the alpha channel to apply masks, whereas Cairo
only handles alpha. The only way to fix this is to find a "luminance-to-alpha"
filter.


Even-Odd Rule
=============

- ``masking-path-05-f``

The even-odd rule must be handled by path according to the SVG
specification. Unfortunately, Cairo clips all the paths with the same fill
rule.


Clip Path Intersections
=======================

- ``masking-path-07-b``

This test is a hard one, and a lot of things fail here including nested
clip-path properties and use/clipPath inherited attributes.

======
 Text
======

.. info::

   The ``text.py`` file has to be rewritten. The glyphs must be drawn one by
   one in order to handle new features such as text on paths and glyph rotation.


Text on a Path
==============

- ``text-path-02-b``
- ``text-align-04-b``

`Text on a path <http://www.w3.org/TR/SVG/text.html#TextOnAPath>`_ doesn't work
when the text must be drawn after or before the path. This has to be handled
when the module is rewritten.


Rotation
========

- ``tspan04``
- ``tspan05``

`Glyph rotation
<http://www.w3.org/TR/SVG/text.html#TextElementRotateAttribute>`_ is not
managed at all. This has to be handled when the module is rewritten.


Reference
=========

- ``text-ws-03-t``

`Character reference
<http://www.w3.org/TR/SVG/text.html#TextElementRotateAttribute>`_ is not
handled correctly and raises errors. This has to be handled when the module is
rewritten.


Decoration and Spacing
======================

- ``textdecoration01``
- ``text-ws-03-t``

Text decoration, spacing, kerning, and various other features are not handled
in Cairo, and thus cannot be handled in CairoSVG. One solution to solve this
problem would be to use Pango, but that's a huge dependency. You can consider
these features as "won't fix".

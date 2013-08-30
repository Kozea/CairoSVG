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

`Text on a path <http://www.w3.org/TR/SVG/text.html#TextOnAPath>`_ still
suffers some little bugs with alignment.


Decoration, Spacing, Bidi, Kerning, Alt Glyphs
==============================================

- ``textdecoration01``
- ``styling-css-05-b``
- other ``text-%*``

Text decoration, kerning, and various other features are not handled
in Cairo, and thus cannot be handled in CairoSVG. One solution to solve this
problem would be to use Pango, but that's a huge dependency. You can consider
these features as "won't fix".

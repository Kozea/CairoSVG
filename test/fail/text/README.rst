======
 Text
======

Decoration, Alignment, Spacing, Bidi, Kerning, Alt Glyphs
=========================================================

- ``textdecoration01``
- ``styling-css-05-b``
- other ``text-%*``

Text decoration, kerning, and various other features are not handled
in Cairo, and thus cannot be handled in CairoSVG. One solution to solve this
problem would be to use Pango, but that's a huge dependency. You can consider
these features as "won't fix".

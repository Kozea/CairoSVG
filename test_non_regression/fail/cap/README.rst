==========
 Line Cap
==========

Square line caps must be drawn with zero-length paths. When no direction is set
to the path (lineto operation with the same begin and end points), cairo does
not draw the caps. The SVG says that the caps must be drawn as if the path is
horizontal, but there's no evident way to know when we're in this situation.

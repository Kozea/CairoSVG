=======
 Cairo
=======

These bugs are caused by cairo.


Line Cap
========

- ``painting-control-04-f``
- ``painting-stroke-10-t``

Square line caps must be drawn with zero-length paths. `Cairo says that it
draws these lines
<http://cairographics.org/documentation/pycairo/2/reference/context.html#cairo.Context.stroke>`_,
but it doesn't.


Radial Gradient
===============

- ``pservers-grad-13-b``

The radial gradients are broken in Cairo if the inner circle is outside the
outer circle.

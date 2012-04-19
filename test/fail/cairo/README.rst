=======
 Cairo
=======

These bugs are caused by cairo.


Radial Gradient
===============

- ``pservers-grad-13-b``

The radial gradients are broken in Cairo if the inner circle is outside the
outer circle.


Painting Stroke
===============

- ``painting-stroke-06-t``

The dashes lengths are not in user-units anymore since 1.12.0. `A bug has been
reported <https://bugs.freedesktop.org/show_bug.cgi?id=48818>` and `a fix has
been committed
<http://cgit.freedesktop.org/cairo/commit/src?id=70fc52cb80f21fff0ba960236f24b997692cce64>`_.

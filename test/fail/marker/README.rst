========
 Marker
========


Missing ``marker`` attributes
=============================

- ``painting-marker-02-f``
- ``painting-marker-05-f``

Many attributes such as ``overflow``, ``markerUnits``, ``ref*`` and ``marker*``
are not handled correctly.


Presentational ``marker`` attribute
===================================

- ``painting-marker-04-f``

The ``marker`` shortand property should not be allowed as a presentational
attribute, but it currently is in CairoSVG.


``display`` attribute
=====================

- ``painting-marker-07-f``

The ``display`` attribute on the marker or its ancestors should be ignored, but
it's currently not in CairoSVG.

=======
 Draft
=======

.. info::

   These tests are or were considered as drafts by the W3C, and we're not sure
   that they should be correcly handled by CairoSVG.


Arcs
====

- ``paths-data-20-f``

This test tries to use the most horrible syntaxes for the `arc command
<http://www.w3.org/TR/SVG/paths.html#PathDataEllipticalArcCommands>`_. But some
of the sytaxes do not follow the `grammar for path data
<http://www.w3.org/TR/SVG/paths.html#PathDataBNF>`_, especially for flags
(defined as "0" or "1" in the BNF).


Units
=====

- ``types-basic-02-f``

This (draft) test looks at the case-(in)sensitivity of the units. As the
reference PNG is broken, there's no need to dig this right now.


Styling
=======

- ``styling-pres-*``

These tests have empty PNG references.


Markers
=======

- ``painting-marker-properties-01-f``

This test seems to be broken, polygons have wrong properties.

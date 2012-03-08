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

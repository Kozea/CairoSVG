=====================
 Project Description
=====================

:Author: Guillaume Ayoub

:Date: 2012-02-17

:Abstract: This document defines the main goals of CairoSVG, what it covers and
 what it does not.

.. contents::

Main Goal
=========

CairoSVG has one main goal: convert SVG to Cairo surfaces, with Pycairo as only
dependency. This requirement makes CairoSVG independant from X, Glib or GTK+.


What CairoSVG Is
================

SVG Parser
----------

The main part of CairoSVG is a SVG parser, trying to follow the `SVG 1.1
Recommandation from the W3C <http://www.w3.org/TR/SVG11/>`_.

Cairo Surface Exporter
----------------------

Once parsed, the result is drawn to a Cairo surface that can be exported to
various formats: PDF, PostScript, PNG and even SVG.


What CairoSVG Is not and will not Be
====================================

Perfect SVG Reader
------------------

CairoSVG can only rely on Cairo to draw, and is then limited in various ways by
this library, including the lack of raster filters, no logical color operations
and a poor font management.

Many languages that must be supported by SVG readers are not supported by
CairoSVG, including ECMAScript and XSLT. External CSS is supported with
optional dependancies.

CairoSVG assumes that the input SVG files are perfect SVG files. If one SVG is
not well formed, CairoSVG can do anything, including not rendering at
all. Managing errors, wrong values and fallbacks is difficult, requires a lot
of code and is not that fun: not managing the errors is better than only
managing some of them.

No animation is supported in CairoSVG.

Image Converter
---------------

CairoSVG only reads SVG. A lot of other softwares are already able to read and
write a lot of other image formats, CairoSVG will not be one of them.

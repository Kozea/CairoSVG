=================
 SVG 1.1 Support
=================

:Author: Guillaume Ayoub

:Date: 2011-12-09

:Abstract: This document presents the supported and unsupported features of SVG
 1.1 in CairoSVG.

.. contents::

Here is the support status of the different elements of SVG 1.1 (2\ :sup:`nd`
edition). The different sections correspond to those from `the specification
<http://www.w3.org/TR/SVG11/>`_.


Introduction
============

About SVG
---------

No animations are supported in CairoSVG, as the output formats are mainly
static. More generally, no real DOM support is offered, highly limiting the
possibility of implementing features such as CSS or JavaScript support.


SVG MIME type, file name extension and Macintosh file type
----------------------------------------------------------

CairoSVG does not directly read gzip-compressed SVG files. It does not rely on
the ``.svg`` input file extension.


SVG Namespace, Public Identifier and System Identifier
------------------------------------------------------

CairoSVG does not rely on the namespace URL, public identifier and system
identifier URL. No DTD validation is provided.


Compatibility with Other Standards Efforts
------------------------------------------

Based on ElementTree, CairoSVG needs a real XML path and is not fault tolerant
when parsing the XML. However, basic XML features such as namespaces are
internally used. XLink is partially supported and should work for the standard
usage.

CSS, XSLT, DOM, XML-SS, SMIL and Web Accessibility are not supported at all.

The basic Unicode features are supported, and should work for latin
left-to-right-written languages. Other configurations are not tested yet.


Terminology
-----------

This document is not an RFC.


Definitions
-----------

This document does not really follow the definitions coming from this part (see
previous chapter).




Concepts
========

Explaining the name: SVG
------------------------

CairoSVG respects the scalable and vector parts of the format, when
possible. PDF and PostScript formats allow vector graphics, and Cairo exports
to these formats waithout rastering when possible.

Based on ElementTree, CairoSVG needs SVG files that are XML tree, and is not
fault-tolerent. Namespaces are well supported.

CSS is not supported at all, but using a simple CSS pre-processor before
CairoSVG (transforming the CSS into XML attributes) is possible.


Important SVG concepts
----------------------

Raster effects are not supported, because they are not supported by Cairo.

Fonts are also managed by Cairo, known to be just a "toy" about fonts. Pango
would be a much better choice, but it is a heavy dependency. Nevertheless,
fonts can be selected in PDF documents.

Animations are not supported.


Options for using SVG in Web pages
----------------------------------

CairoSVG can generate standard Cairo surfaces that can be used in Cairo-based
web clients such as `WeasyPrint <http://weasyprint.org/>`_.




Rendering Model
===============

Introduction
------------

CairoSVG generally follows the rendering model described by the specification.


The painters model
------------------

The painter model of Cairo, used by CairoSVG, is the same as the one from the
specification. This includes alpha blending.


Rendering Order
---------------

The elements are rendered in the order of the SVG document.


How groups are rendered
-----------------------

Opacity values of groups are applied to the elements
of the group. Filter effects and masks are not supported.


How elements are rendered
-------------------------

Opacity values of elements are applied. Filter effects and masks are not
supported.


Types of graphics elements
--------------------------

1 Painting shapes and text
~~~~~~~~~~~~~~~~~~~~~~~~~~

Elements are filled and stoked. Filling supports plain colors, simple gradients
and simple patterns. Stoking only supports plain colors. Transparency is
supported for both filling and stoking.

2 Painting raster images
~~~~~~~~~~~~~~~~~~~~~~~~

Included raster images are not supported.


Filtering painted regions
-------------------------

Filter effects are not supported.


Clipping, masking and object opacity
------------------------------------

Clipping and masking are not supported.

Transparency, with simple alpha blending, is supported for semi-transparent
colors and opacity values.

Parent Compositing
------------------

Transparency for the parent document are supported as long as the output format
supports it. Semi-transparent PNGs can be generated.




Basic Data Types and Interfaces
===============================

Syntax
------

Thank you EBNF.


Basic data types
----------------

Angles are only supported when given in degrees, without explicit unit.

Colors are supported with ``rgb()``, ``rgba()``, ``#RGB``, and ``#RRGGBB``
forms. The not standard ``#RGBA`` and ``#RRGGBBAA`` forms are also
supported. Color keyword names are supported.

Frequencies are not supported.

Standard URI and IRI forms are supported, including fragment identifiers.

Numbers are supported, including integers and floats with the negative
values. Exponents are not supported.

Lengths are supported, with ``mm``, ``cm``, ``in``, ``pt`` and ``pc`` units.

Lists of various values are supported.

Percentages are not supported.

Times are not supported.


Real number precision
---------------------

The real number precision is the same as the one of Python.


Recognized color keyword names
------------------------------

Color keyword names are supported.


Basic DOM interfaces
--------------------

CairoSVG uses ElementTree internally, and has no real DOM interface.


Document Structure
==================



Styling
=======



Coordinate Systems, Transformations and Units
=============================================



Paths
=====



Basic Shapes
============



Text
====



Painting: Filling, Stroking and Marker Symbols
==============================================



Color
=====



Gradients and Patterns
======================



Clipping, Masking and Compositing
=================================



Filter Effects
==============



Interactivity
=============



Linking
=======



Scripting
=========



Animation
=========



Fonts
=====



Metadata
========



Backwards Compatibility
=======================



Extensibility
=============

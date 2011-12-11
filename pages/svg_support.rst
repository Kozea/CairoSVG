=================
 SVG 1.1 Support
=================

:Author: Guillaume Ayoub

:Date: 2011-12-09

:Abstract: This document presents the supported and unsupported features of SVG
 1.1 in CairoSVG.

.. contents::

Here is the support status of the different elements of SVG 1.1 (2\ :sup:`nd`
edition). The different sections correspond to those from the specification.


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
web clients such as `WeasyPrint <http://weasyprint.org/>`_




Rendering Model
===============



Basic Data Types and Interfaces
===============================



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

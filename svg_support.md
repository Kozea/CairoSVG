---
layout: page
title: SVG 1.1 Support
permalink: /svg_support/
---

Here is the support status of the different elements of SVG 1.1. The different
sections correspond to those from
[the specification](http://www.w3.org/TR/SVG11/). You'll find more simple
information and tips on the [documentation page](/documentation/).


## Introduction

### About SVG

No animations are supported in CairoSVG, as the output formats are mainly
static. More generally, no real DOM support is offered, highly limiting the
possibility of implementing features such as JavaScript support.


### SVG MIME type, file name extension and Macintosh file type

CairoSVG can directly read gzip-compressed SVG files, relying on the `.svg`
or `.svgz` input file extension to know if the file should be uncompressed.


### SVG Namespace, Public Identifier and System Identifier

CairoSVG does not rely on the namespace URL, public identifier and system
identifier URL. No DTD validation is provided.


### Compatibility with Other Standards Efforts

Based on ElementTree, CairoSVG needs a real XML path and is not fault tolerant
when parsing the XML. However, basic XML features such as namespaces are
internally used. XLink is partially supported and should work for the standard
usage.

Inline and external CSS is basically supported.

External XSLT, DOM, XML-SS, SMIL and Web Accessibility are not supported at
all.

The basic Unicode features are supported, and should work for latin
left-to-right-written languages. Other configurations are not tested yet.


### Terminology

This document is not an RFC.


### Definitions

This document does not really follow the definitions coming from this part (see
previous chapter).



## Concepts

### Explaining the name: SVG

CairoSVG respects the scalable and vector parts of the format, when
possible. PDF and PostScript formats allow vector graphics, and Cairo exports
to these formats without rastering when possible.

Based on ElementTree or lxml, CairoSVG needs SVG files that are XML tree, and
is not fault-tolerent. Namespaces are well supported.

Inline CSS is supported. External stylesheets are also supported when the
tinycss and lxml libraries are available.


### Important SVG concepts

Raster effects are not supported, because they are not supported by Cairo.

Fonts are also managed by Cairo, known to be just a 'toy' about fonts. Pango
would be a much better choice, but it is a heavy dependency. Nevertheless,
fonts can be selected in PDF documents.

Animations are not supported.


### Options for using SVG in Web pages

CairoSVG can generate standard Cairo surfaces that can be used in Cairo-based
web clients such as [WeasyPrint](http://weasyprint.org/).



## Rendering Model

### Introduction

CairoSVG generally follows the rendering model described by the specification.


### The painters model

The painter model of Cairo, used by CairoSVG, is the same as the one from the
specification. This includes alpha blending.


### Rendering Order

The elements are rendered in the order of the SVG document.


### How groups are rendered

Opacity values of groups are applied to the rendered inner elements. Simple
masks, clips and filters are supported.


### How elements are rendered

Opacity values of elements are applied. Simple masks, clips and filters are
supported.


### Types of graphics elements

#### Painting shapes and text

Elements are filled and stroked. Filling and stroking support plain colors,
simple gradients and simple patterns, with or without opacity.

#### Painting raster images

Included raster images are supported by the
[Pillow](http://python-pillow.github.io/) package.


### Filtering painted regions

3 filter effects are supported:

- feBlend,
- feFlood,
- feOffset.


### Clipping, masking and object opacity

Path clipping and alpha masking are supported. Clip and overflow of new
viewports is not supported. Masks based on luminance are not supported.

Transparency, with simple alpha blending, is supported for semi-transparent
colors and opacity values.

### Parent Compositing

Transparency for the parent document are supported as long as the output format
supports it. Semi-transparent PNGs can be generated.



## Basic Data Types and Interfaces

### Syntax

Thank you EBNF.


### Basic data types

Angles are only supported when given in degrees, without explicit unit.

Colors are supported with `rgb()`, `rgba()`, `#RGB`, and `#RRGGBB`
forms. Color keyword names are supported.

Frequencies are not supported.

Standard URI and IRI forms are supported, including fragment identifiers.

Numbers are supported, including exponents, integers and floats with the
negative values.

Lengths are supported, with `mm`, `cm`, `in`, `pt`, `pc`, `em`,
`ex` and `%` units.

Lists of various values are supported.

Times are not supported.


### Real number precision

The real number precision is the same as the one of Python.


### Recognized color keyword names

Color keyword names are supported.


### Basic DOM interfaces

CairoSVG uses ElementTree internally, and has no real DOM interface.



## Document Structure

### Defining an SVG document fragment: the `svg` element

The `svg` tag is supported. In CairoSVG, `svg` tags that are direct
children of the root `svg` tag are considered as pages in multi-pages output
formats (PDF and PS).


### Grouping: the `g` element

The `g` tag is supported.


### Defining content for reuse, and the `defs` element

The `defs` tag is supported for markers, gradients, patterns and paths reused
in the document.


### The `desc` and `title` elements

The `desc` and `title` tag are not supported.


### The `symbol` element

The `symbol` tag is not supported.


### The `use` element

The `use` tag supports local and distant (i.e. available through HTTP)
external SVG files.


### The `image` element

The `image` tag is supported by Pystacia.


### Conditional processing

Conditional processing is not supported.


### Specifying whether external resources are required for proper rendering

The `externalResourcesRequired` attribute is not supported.


### Common attributes

The `id` attribute is supported.

The `xml:base` attribute is supported for images.


### DOM interfaces

The DOM interfaces are not supported.



## Styling

Styling cannot be done with XSL. Inline and external CSS are basically
supported.

Here are some properties that can be used as XML attributes:

Font properties:

- `font`: not supported
- `font-family`: basically supported
- `font-size`: basically supported
- `font-size-adjust`: not supported
- `font-stretch`: not supported
- `font-style`: basically supported
- `font-variant`: not supported
- `font-weight`: basically supported

Text properties:

- `direction`: not supported
- `letter-spacing`: not supported
- `text-decoration`: not supported
- `unicode-bidi`: not supported
- `word-spacing`: not supported

Other properties for visual media:

- `clip`: not supported
- `cursor`: not supported
- `display`: supported
- `overflow`: not supported
- `visibility`: supported

Clipping, Masking and Compositing properties:

- `clip-path`: supported
- `clip-rule`: supported
- `mask`: basically supported
- `opacity`: supported

Filter Effects properties:

- `enable-background`: not supported
- `filter`: feBlend, feFlood and feOffset supported
- `flood-color`: not supported
- `flood-opacity`: not supported
- `lighting-color`: not supported

Gradient properties:

- `stop-color`: supported
- `stop-opacity`: supported

Interactivity properties:

- `pointer-events`: not supported

Color and Painting properties:

- `color-interpolation`: not supported
- `color-interpolation-filters`: not supported
- `color-profile`: not supported
- `color-rendering`: not supported
- `fill`: supported
- `fill-opacity`: supported
- `fill-rule`: supported
- `image-rendering`: not supported
- `marker`: basically supported
- `marker-end`: basically supported
- `marker-mid`: basically supported
- `marker-start`: basically supported
- `shape-rendering`: supported
- `stroke`: supported
- `stroke-dasharray`: supported
- `stroke-dashoffset`: supported
- `stroke-linecap`: supported
- `stroke-linejoin`: supported
- `stroke-miterlimit`: supported
- `stroke-opacity`: supported
- `stroke-width`: supported
- `text-rendering`: supported

Text properties:

- `alignment-baseline`: basically supported
- `baseline-shift`: not supported
- `dominant-baseline`: not supported
- `glyph-orientation-horizontal`: not supported
- `glyph-orientation-vertical`: not supported
- `kerning`: not supported
- `text-anchor`: supported
- `writing-mode`: not supported



## Coordinate Systems, Transformations and Units

### Introduction

CairoSVG renders its output on finite rectangular regions called viewport in
the W3 recommendation, and Cairo surfaces in the application.

The viewport size must be given in the tag, as no negotiation process can be
realized with the parent surface.

The coordinates transformations are correctly handled by CairoSVG, including
nested transformations. Most of the transformations applied to external
elements, including the ones in the gradients and the patterns, are supported.


### The initial viewport

As the pages are not embedded, no negotiation process is possible when trying
to determine the pages sizes.


### The initial coordinate system

CairoSVG follows the recommendation about the initial coordinate system.


### Coordinate system transformations

The coordinate system transformation given by the `viewBox` is correctly
managed by CairoSVG. Rotations, translations and skews are correctly managed.


### Nested transformations

Transformations can be nested in CairoSVG.


### The `transform` attribute

The `transform` attribute parses and applies the `matrix`, `translate`,
`scale`, `rotate`, `skewX` and `skewY` operations.


### The `viewBox` attribute

The `viewBox` attribute is supported.


### The `preserveAspectRatio` attribute

The `preserveAspectRatio` attribute is supported for `svg` elements, and
not supported the other elements.


### Establishing a new viewport

Only the `svg` element establishes a new viewport in CairoSVG.


### Units

`mm`, `cm`, `in`, `pt`, `pc`, `em`, `ex` and percentages units
are supported.


### Object bounding box units

The `objectBoundingBox` attribute is not supported.


### Intrinsic sizing properties of the viewport of SVG content

When the `viewBox` attribute is set to `none`, and no `width` or
`height` is given, the intrinsic sizing properties of the viewport is not
set, and the behaviour of CairoSVG is undetermined.


### Geographic coordinate systems

No geographic coordinate system is managed in CairoSVG.


### The `svg:transform` attribute

The `transform` attribute is correctly handled by CairoSVG.


### DOM interfaces

The DOM interfaces are not supported.


## Paths

### Introduction

Paths are supported, including subpaths.


### The `path` element

The main path attributes are supported.


### Path data

The `moveto`, `closepath`, `lineto`, `curveto`, quadratic Bézier
`curveto` and `arcto` commands are supported.


### Distance along a path

Distance is calculated for text on a path.


### DOM interfaces

The DOM interfaces are not supported.


## Basic Shapes

### Introduction

Basic shapes (rectangles, circles, ellipses, lines, polylines and polygons) are
supported.


### The `rect` element

Rectangles, including rounded corners, are supported.


### The `circle` element

Circles are supported.


### The `ellipse` element

Ellipses are supported.


### The `line` element

Lines are supported.


### The `polyline` element

Polylines are supported.


### The `polygon` element

Polygons are supported.


### DOM interfaces

The DOM interfaces are not supported.


## Text

### Introduction

The main features of text rendering are supported. The `text` and `tspan`
tags are supported.


### Characters and their corresponding glyphs

Characters are rendered by Cairo, text rendering relies on its simple rendering
engine. There should be no ligatures, composite characters or glyph
supstitutions.


### Fonts, font tables and baselines

There's no real baseline management with Cairo. The really simple vertical
management doesn't rely on the baseline.


### The `text` element

The `text` element is supported, including its `rotate` attribute.


### The `tspan` element

The `tspan` element is supported, including its `rotate` attribute.


### The `tref` element

The `tref` element is supported.


### Text layout

Simple text layout is managed for latin scripts, but not for bidirectional and
vertical scripts.


### Text rendering order

The glyphs are not rendered independently.


### Alignment properties

Horizontal text alignment is supported for latin scripts.

Vertical text alignment is basically supported, but does no rely on the
baseline and is only capable of top, middle or bottom alignment.


### Font selection properties

The `font-family`, `font-size`, `font-style` and `font-weight` are
basically supported, and should work as expected for common cases. The other
attributes, including the `font` shorthand, are not supported.


### Spacing properties

The spacing properties are not supported.


### Text decoration

Text decoration is not supported.


### Text on a path

Text on a path is supported, including the `startOffset` attribute.


### Alternate glyphs

Alternate glyphs are not supported.


### White space handling

White space are correctly handled and follow the rules given by the
`xml:space` attribute.


### Text selection and clipboard operations

Text selection is possible for PDF documents generated by CairoSVG, when the
text is rendered with no extra effects including stroke and transformations.


### DOM interfaces

The DOM interfaces are not supported.


## Painting: Filling, Stroking and Marker Symbols

### Introduction

Filling and stroking operations are supported for paths, texts and basic
shapes. Markers are supported for paths, polylines, polygons and lines.


### Specifying paint

Painting values are supported, with no ICC support. Gradients ant patterns are
supported.


### Fill properties

Filling operations are supported, including the `fill-rule` property.


### Stroke properties

Stroking operations are supported, including all the `stroke-*` properties.


### Controlling visibility

The `display` and `visibility` properties are supported.


### Markers

Simple markers are supported, including the `marker-*` and `orient`
attributes. Clipping thanks to the `overflow` property is not supported.


### Rendering properties

Color interpolation and rendering properties are not supported. Shape, text and
image rendering options are supported.


### Inheritance of painting properties

Painting properties are supported.


### DOM interfaces

The DOM interfaces are not supported.


## Color

### Introduction

CairoSVG handles the RGB part of this module.


### The `color` property

The property as defined by the CSS2 specification is correctly handled.


### Color profile descriptions

Color profiles are not handled.


### DOM interfaces

The DOM interfaces are not supported.


## Gradients and Patterns

### Introduction

Gradients are generally correctly handled whereas patterns are poorly handled.


### Gradients

Gradients are correctly handled, as long as Cairo can handle them. Some little
details may not be rendered correctly, but you can rely on most of the
generally used features.


### Patterns

Patterns are poorly handled. Naive pattens are rendered, but simple features
such as the `viewBox` property are ignored.


### DOM interfaces

The DOM interfaces are not supported.


## Clipping, Masking and Compositing

### Introduction

Some of the clipping and masking features are handled. Simple alpha compositing
and opacity are partially supported,


### Simple alpha compositing

Alpha compositing is supported in Cairo, but `color-interpolation` and
`color-rendering` properties are ignored.


### Clipping paths

Path clipping is handled, but new viewports are not clipped.


### Masking

Masking is handled with alpha-based masks, but not with luminance-based ones.


### Opacity

The different `*-opacity` parameters are correctly handled.


### DOM interfaces

The DOM interfaces are not supported.


## Filter Effects

3 filter effects are supported:

- feBlend,
- feFlood,
- feOffset.


## Interactivity

No interactivity features are handled in CairoSVG.


## Linking

Linking is not handled.


## Scripting

Scripting is not handled.


## Animation

Animations are not handled.


## Fonts

### Introduction

Simple font features, as described by the CSS2 specification, are handled, but
Cairo has a poor support of complex features about fonts.

SVG fonts are not handled at all.


### Overview of SVG fonts

SVG fonts are not handled.


### The `font` element

The `font` element is ignored.


### The `glyph` element

The `glyph` element is ignored.


### The `missing-glyph` element

The `missing-glyph` element is ignored.


### Glyph selection rules

Glyphs are not handled.


### The `hkern` and `vkern` elements

The `hkern` and `vkern` elements are ignored.


### Describing a font

Fonts, as defined by CSS2, are naively handled. Nevertheless, there is no real
strategy to choose a font from its name, CairoSVG relies on Cairo for this
choice.


### DOM interfaces

The DOM interfaces are not supported.


## Metadata

Metadata are ignored.

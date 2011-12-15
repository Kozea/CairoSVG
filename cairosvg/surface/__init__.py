# -*- coding: utf-8 -*-
# This file is part of CairoSVG
# Copyright © 2010-2011 Kozea
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CairoSVG.  If not, see <http://www.gnu.org/licenses/>.

"""
Cairo surface creators.

"""

import abc
import cairo
import io
import math
import os

from .colors import color
from .defs import gradient_or_pattern, parse_def
from .helpers import node_format, normalize
from .path import PATH_TAGS
from .tags import TAGS
from .units import size


class Surface(object):
    """Cairo dummy surface.

    This class may be overriden to create surfaces with real output
    capabilities.

    """
    def __init__(self, tree):
        """Create the surface from ``tree``."""
        self.cairo = None
        self.context = None
        self.cursor_position = 0, 0
        self.total_width = 0
        self.markers = {}
        self.gradients = {}
        self.patterns = {}
        self.paths = {}
        self._old_parent_node = self.parent_node = None
        self.bytesio = io.BytesIO()
        self._width = None
        self._height = None
        self._create_surface(tree)
        self.draw(tree)

    def _create_surface(self, tree):
        """Create a cairo surface.

        A method overriding this one must create ``self.cairo`` and
        ``self.context``.

        """
        self._width, self._height, viewbox = node_format(tree)
        self.cairo = cairo.SVGSurface(None, self._width, self._height)
        self.context = cairo.Context(self.cairo)
        self._set_context_size(self._width, self._height, viewbox)
        self.context.move_to(0, 0)

    def _set_context_size(self, width, height, viewbox):
        """Set the context size."""
        if viewbox:
            x, y, x_size, y_size = viewbox
            x_ratio, y_ratio = width / x_size, height / y_size
            if x_ratio > y_ratio:
                self.context.translate((width - x_size * y_ratio) / 2, 0)
                self.context.scale(y_ratio, y_ratio)
                self.context.translate(-x, -y / y_ratio * x_ratio)
            elif x_ratio < y_ratio:
                self.context.translate(0, (height - y_size * x_ratio) / 2)
                self.context.scale(x_ratio, x_ratio)
                self.context.translate(-x / x_ratio * y_ratio, -y)
            else:
                self.context.scale(x_ratio, y_ratio)
                self.context.translate(-x, -y)

    def read(self):
        """Read the surface content."""
        self.cairo.finish()
        value = self.bytesio.getvalue()
        self.bytesio.close()
        return value

    def draw(self, node, stroke_and_fill=True):
        """Draw ``node`` and its children."""
        # Do not draw defs
        if node.tag == "defs":
            for child in node.children:
                parse_def(self, child)
            return

        node.tangents = [None]
        node.pending_markers = []

        self._old_parent_node = self.parent_node
        self.parent_node = node

        self.context.save()
        self.context.move_to(size(node.get("x")), size(node.get("y")))

        # Transform the context according to the ``transform`` attribute
        if node.get("transform"):
            transformations = node["transform"].split(")")
            for transformation in transformations:
                for ttype in (
                        "scale", "translate", "matrix", "rotate", "skewX",
                        "skewY"):
                    if ttype in transformation:
                        transformation = transformation.replace(ttype, "")
                        transformation = transformation.replace("(", "")
                        transformation = normalize(transformation).strip()
                        transformation += " "
                        values = []
                        while transformation:
                            value, transformation = \
                                transformation.split(" ", 1)
                            values.append(size(value))
                        if ttype == "matrix":
                            matrix = cairo.Matrix(*values)
                            self.context.set_matrix(matrix)
                        elif ttype == "rotate":
                            matrix = self.context.get_matrix()
                            self.context.rotate(math.radians(float(values[0])))
                        elif ttype == "skewX":
                            matrix = self.context.get_matrix()
                            degree = math.radians(float(values[0]))
                            mtrx = cairo.Matrix(
                                matrix[0], matrix[1], matrix[2] + degree,
                                matrix[3], matrix[4], matrix[5])
                            self.context.set_matrix(mtrx)
                        elif ttype == "skewY":
                            matrix = self.context.get_matrix()
                            degree = math.radians(float(values[0]))
                            mtrx = cairo.Matrix(
                                matrix[0], matrix[1] + degree, matrix[2],
                                matrix[3], matrix[4], matrix[5])
                            self.context.set_matrix(mtrx)
                        else:
                            if len(values) == 1:
                                values = 2 * values
                            getattr(self.context, ttype)(*values)

        if node.tag in PATH_TAGS:
            # Set 1 as default stroke-width
            if not node.get("stroke-width"):
                node["stroke-width"] = "1"

        # Set node's drawing informations if the ``node.tag`` method exists
        line_cap = node.get("stroke-linecap")
        if line_cap == "square":
            self.context.set_line_cap(cairo.LINE_CAP_SQUARE)
        if line_cap == "round":
            self.context.set_line_cap(cairo.LINE_CAP_ROUND)

        join_cap = node.get("stroke-linejoin")
        if join_cap == "round":
            self.context.set_line_join(cairo.LINE_JOIN_ROUND)
        if join_cap == "bevel":
            self.context.set_line_join(cairo.LINE_JOIN_BEVEL)

        miter_limit = float(node.get("stroke-miterlimit", 4))
        self.context.set_miter_limit(miter_limit)

        if node.tag in TAGS:
            TAGS[node.tag](self, node)

        # Get stroke and fill opacity
        opacity = float(node.get("opacity", 1))
        stroke_opacity = opacity * float(node.get("stroke-opacity", 1))
        fill_opacity = opacity * float(node.get("fill-opacity", 1))

        # Manage dispaly and visibility
        display = node.get("display", "inline") != "none"
        visible = display and (node.get("visibility", "visible") != "hidden")

        if stroke_and_fill and visible:
            # Fill
            if "url(#" in node.get("fill", ""):
                gradient_or_pattern(self, node)
            else:
                if node.get("fill-rule") == "evenodd":
                    self.context.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
                self.context.set_source_rgba(
                    *color(node.get("fill", "black"), fill_opacity))
                self.context.fill_preserve()

            # Stroke
            self.context.set_line_width(size(node.get("stroke-width")))
            self.context.set_source_rgba(
                *color(node.get("stroke"), stroke_opacity))
            self.context.stroke()

        # Draw children
        if display:
            for child in node.children:
                self.draw(child, stroke_and_fill)

        if not node.root:
            # Restoring context is useless if we are in the root tag, it may
            # raise an exception if we have multiple svg tags
            self.context.restore()

        self.parent_node = self._old_parent_node


class MultipageSurface(Surface):
    """Cairo abstract surface managing multi-page outputs.

    Classes overriding :class:`MultipageSurface` must have a ``surface_class``
    class attribute corresponding to the cairo surface class.

    """
    __metaclass__ = abc.ABCMeta
    surface_class = NotImplementedError

    def _create_surface(self, tree):
        width, height, viewbox = node_format(tree)
        if "svg" in tuple(child.tag for child in tree.children):
            # Real svg pages are in this root svg tag, create a fake surface
            self.context = cairo.Context(
                self.surface_class(os.devnull, width, height))
        else:
            self.cairo = self.surface_class(self.bytesio, width, height)
            self.context = cairo.Context(self.cairo)
            self._set_context_size(width, height, viewbox)
            self.cairo.set_size(width, height)
            self.context.move_to(0, 0)

    def svg(self, node):
        """Draw a svg ``node`` with multi-page support."""
        if not node.root:
            width, height, viewbox = node_format(node)
            if self.cairo:
                self.cairo.show_page()
            else:
                self.context.restore()
                self.cairo = self.surface_class(self.bytesio, width, height)
                self.context = cairo.Context(self.cairo)
                self.context.save()
            self._set_context_size(width, height, viewbox)
            self.cairo.set_size(width, height)


class PDFSurface(MultipageSurface):
    """Cairo PDF surface."""
    surface_class = cairo.PDFSurface


class PSSurface(MultipageSurface):
    """Cairo PostScript surface."""
    surface_class = cairo.PSSurface


class OnepageSurface(Surface):
    """Cairo abstract surface managing one page outputs.

    Classes overriding :class:`OnepageSurface` must have a ``self._width`` and
    a ``self._height`` set in ``self._create_surface``.

    """
    __metaclass__ = abc.ABCMeta
    _width = NotImplementedError
    _height = NotImplementedError

    @property
    def width(self):
        """Surface width."""
        return self._width

    @property
    def height(self):
        """Surface height."""
        return self._height


class PNGSurface(OnepageSurface):
    """Cairo PNG surface."""
    def _create_surface(self, tree):
        width, height, viewbox = node_format(tree)

        # The image size has integer width and height
        self._width, self._height = int(width), int(height)
        self.cairo = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self._width, self._height)

        # The context size has floating width and height
        self.context = cairo.Context(self.cairo)
        self._set_context_size(width, height, viewbox)
        self.context.move_to(0, 0)

    def read(self):
        """Read the PNG surface content."""
        self.cairo.write_to_png(self.bytesio)
        return super(PNGSurface, self).read()

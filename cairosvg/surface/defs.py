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
Externally defined elements managers.

This module handles gradients and patterns.

"""

import cairo

from .colors import color
from .helpers import filter_fill_content, node_format
from .units import size
from ..parser import Tree


def parse_def(surface, node):
    """Parse the SVG definitions."""
    if node.tag == "marker":
        surface.markers[node["id"]] = node
    if "gradient" in node.tag.lower():
        surface.gradients[node["id"]] = node
    if "pattern" in node.tag.lower():
        surface.patterns[node["id"]] = node
    if "path" in node.tag:
        surface.paths[node["id"]] = node


def gradient_or_pattern(surface, node):
    """Gradient or pattern color."""
    name = filter_fill_content(node)
    if name in surface.gradients:
        return gradient(surface, node)
    elif name in surface.patterns:
        return pattern(surface, node)


def gradient(surface, node):
    """Gradients colors."""
    gradient = filter_fill_content(node)
    gradient_node = surface.gradients[gradient]

    x = float(size(node.get("x")))
    y = float(size(node.get("y")))
    height = float(size(node.get("height")))
    width = float(size(node.get("width")))
    x1 = float(gradient_node.get("x1", x))
    x2 = float(gradient_node.get("x2", x + width))
    y1 = float(gradient_node.get("y1", y))
    y2 = float(gradient_node.get("y2", y + height))

    # TODO: manage percentages for default values
    if gradient_node.tag == "linearGradient":
        linpat = cairo.LinearGradient(x1, y1, x2, y2)
        for child in gradient_node.children:
            offset = child.get("offset")
            stop_color = color(
                child.get("stop-color"), child.get("stop-opacity", 1))
            offset = child.get("offset")
            if "%" in offset:
                offset = float(offset.strip("%")) / 100
            linpat.add_color_stop_rgba(float(offset), *stop_color)
        surface.context.set_source(linpat)
        surface.context.fill_preserve()
    elif gradient_node.tag == "radialGradient":
        r = float(gradient_node.get("r"))
        cx = float(gradient_node.get("cx"))
        cy = float(gradient_node.get("cy"))
        fx = float(gradient_node.get("fx", cx))
        fy = float(gradient_node.get("fy", cy))
        radpat = cairo.RadialGradient(fx, fy, 0, cx, cy, r)

        for child in gradient_node.children:
            offset = child.get("offset")
            if "%" in offset:
                offset = float(offset.strip("%")) / 100
            stop_color = color(
                child.get("stop-color"), child.get("stop-opacity", 1))
            radpat.add_color_stop_rgba(float(offset), *stop_color)
        surface.context.set_source(radpat)
        surface.context.fill_preserve()


def linearGradient(surface, node):
    """Store a linear gradient definition."""
    parse_def(surface, node)


def radialGradient(surface, node):
    """Store a radial gradient definition."""
    parse_def(surface, node)


def pattern(surface, node):
    """Draw a pattern image."""
    pattern = filter_fill_content(node)
    pattern_node = surface.patterns[pattern]
    if pattern_node.tag == "pattern":
        pattern_surface = type(surface)(pattern_node)
        pattern = cairo.SurfacePattern(pattern_surface.cairo)
        pattern.set_extend(cairo.EXTEND_REPEAT)
        surface.context.set_source(pattern)
        surface.context.fill_preserve()


def use(surface, node):
    """Draw the content of another SVG file."""
    surface.context.save()
    surface.context.translate(size(node.get("x")), size(node.get("y")))
    if "x" in node:
        del node["x"]
    if "y" in node:
        del node["y"]
    if "viewBox" in node:
        del node["viewBox"]
    href = node.get("{http://www.w3.org/1999/xlink}href")
    tree = Tree(href, node)
    surface._set_context_size(*node_format(tree))
    surface.draw(tree)
    surface.context.restore()
    # Restore twice, because draw does not restore at the end of svg tags
    surface.context.restore()

# -*- coding: utf-8 -*-
# This file is part of CairoSVG
# Copyright © 2010-2012 Kozea
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with CairoSVG.  If not, see <http://www.gnu.org/licenses/>.

"""
Externally defined elements managers.

This module handles gradients and patterns.

"""

import cairo
from math import radians

from .colors import color
from .helpers import (
    filter_fill_content, node_format, preserve_ratio, urls, transform)
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
    gradient_node = surface.gradients[filter_fill_content(node)]

    x = float(size(surface, node.get("x"), "x"))
    y = float(size(surface, node.get("y"), "y"))
    height = float(size(surface, node.get("height"), "x"))
    width = float(size(surface, node.get("width"), "y"))
    x1 = float(gradient_node.get("x1", x))
    x2 = float(gradient_node.get("x2", x + width))
    y1 = float(gradient_node.get("y1", y))
    y2 = float(gradient_node.get("y2", y + height))

    transform(surface, gradient_node.get("gradientTransform"))

    if gradient_node.tag == "linearGradient":
        linpat = cairo.LinearGradient(x1, y1, x2, y2)
        for child in gradient_node.children:
            stop_color = color(
                child.get("stop-color"), float(child.get("stop-opacity", 1)))
            offset = size(surface, child.get("offset"), 1)
            linpat.add_color_stop_rgba(offset, *stop_color)
        surface.context.set_source(linpat)
    elif gradient_node.tag == "radialGradient":
        r = float(gradient_node.get("r"))
        cx = float(gradient_node.get("cx"))
        cy = float(gradient_node.get("cy"))
        fx = float(gradient_node.get("fx", cx))
        fy = float(gradient_node.get("fy", cy))
        radpat = cairo.RadialGradient(fx, fy, 0, cx, cy, r)

        for child in gradient_node.children:
            offset = size(surface, child.get("offset"), 1)
            stop_color = color(
                child.get("stop-color"), child.get("stop-opacity", 1))
            radpat.add_color_stop_rgba(float(offset), *stop_color)
        surface.context.set_source(radpat)

    surface.context.fill_preserve()


def linear_gradient(surface, node):
    """Store a linear gradient definition."""
    parse_def(surface, node)


def radial_gradient(surface, node):
    """Store a radial gradient definition."""
    parse_def(surface, node)


def pattern(surface, node):
    """Draw a pattern image."""
    pattern_node = surface.patterns[filter_fill_content(node)]
    transform(surface, pattern_node.get("patternTransform"))

    from . import SVGSurface  # circular import
    pattern_surface = SVGSurface(pattern_node, None, surface.dpi)
    pattern_pattern = cairo.SurfacePattern(pattern_surface.cairo)
    pattern_pattern.set_extend(cairo.EXTEND_REPEAT)
    surface.context.set_source(pattern_pattern)
    surface.context.fill_preserve()
    pattern_surface.finish()


def draw_marker(surface, node, position="mid"):
    """Draw a marker."""
    # TODO: manage markers for other tags than path
    if position == "start":
        node.markers = {
            "start": list(urls(node.get("marker-start", ""))),
            "mid": list(urls(node.get("marker-mid", ""))),
            "end": list(urls(node.get("marker-end", "")))}
        all_markers = list(urls(node.get("marker", "")))
        for markers_list in node.markers.values():
            markers_list.extend(all_markers)
    pending_marker = (
        surface.context.get_current_point(), node.markers[position])

    if position == "start":
        node.pending_markers.append(pending_marker)
        return
    elif position == "end":
        node.pending_markers.append(pending_marker)

    while node.pending_markers:
        next_point, markers = node.pending_markers.pop(0)
        angle1 = node.tangents.pop(0)
        angle2 = node.tangents.pop(0)

        for active_marker in markers:
            if not active_marker.startswith("#"):
                continue
            active_marker = active_marker[1:]
            if active_marker in surface.markers:
                marker_node = surface.markers[active_marker]

                angle = marker_node.get("orient", "0")
                if angle == "auto":
                    angle = float(angle1 + angle2) / 2
                else:
                    angle = radians(float(angle))

                temp_path = surface.context.copy_path()
                current_x, current_y = next_point

                if node.get("markerUnits") == "userSpaceOnUse":
                    base_scale = 1
                else:
                    base_scale = size(
                        surface, surface.parent_node.get("stroke-width"))

                # Returns 4 values
                scale_x, scale_y, translate_x, translate_y = \
                    preserve_ratio(surface, marker_node)

                viewbox = node_format(surface, marker_node)[-1]
                viewbox_width = viewbox[2] - viewbox[0]
                viewbox_height = viewbox[3] - viewbox[1]

                surface.context.new_path()
                for child in marker_node.children:
                    surface.context.save()
                    surface.context.translate(current_x, current_y)
                    surface.context.rotate(angle)
                    surface.context.scale(
                        base_scale / viewbox_width * float(scale_x),
                        base_scale / viewbox_height * float(scale_y))
                    surface.context.translate(translate_x, translate_y)
                    surface.draw(child)
                    surface.context.restore()
                surface.context.append_path(temp_path)

    if position == "mid":
        node.pending_markers.append(pending_marker)


def marker(surface, node):
    """Store a marker definition."""
    parse_def(surface, node)


def use(surface, node):
    """Draw the content of another SVG file."""
    surface.context.save()
    surface.context.translate(
        size(surface, node.get("x"), "x"), size(surface, node.get("y"), "y"))
    if "x" in node:
        del node["x"]
    if "y" in node:
        del node["y"]
    if "viewBox" in node:
        del node["viewBox"]
    href = node.get("{http://www.w3.org/1999/xlink}href")
    tree = Tree(url=href, parent=node)
    surface.set_context_size(*node_format(surface, tree))
    surface.draw(tree)
    surface.context.restore()
    # Restore twice, because draw does not restore at the end of svg tags
    surface.context.restore()

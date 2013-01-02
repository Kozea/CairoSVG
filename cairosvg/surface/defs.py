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
from copy import deepcopy

from .colors import color
from .helpers import node_format, preserve_ratio, urls, transform
from .units import size, UNITS
from ..parser import Tree


def update_def_href(surface, def_name, def_dict):
    """Update the attributes of the def according to its href attribute."""
    def_node = def_dict[def_name]
    href = def_node.get("{http://www.w3.org/1999/xlink}href")
    if href and href[0] == "#" and href[1:] in def_dict:
        new_def_node = deepcopy(def_dict[href[1:]])
        new_def_node.update(def_node)
        def_node = new_def_node
        def_dict[def_name] = def_node


def parse_def(surface, node):
    """Parse the SVG definitions."""
    for def_type in ("marker", "gradient", "pattern", "path", "mask"):
        if def_type in node.tag.lower():
            getattr(surface, def_type + "s")[node["id"]] = node


def gradient_or_pattern(surface, node, name):
    """Gradient or pattern color."""
    if name in surface.gradients:
        update_def_href(surface, name, surface.gradients)
        return draw_gradient(surface, node, name)
    elif name in surface.patterns:
        update_def_href(surface, name, surface.patterns)
        return draw_pattern(surface, node, name)


def marker(surface, node):
    """Store a marker definition."""
    parse_def(surface, node)


def mask(surface, node):
    """Store a mask definition."""
    parse_def(surface, node)


def linear_gradient(surface, node):
    """Store a linear gradient definition."""
    parse_def(surface, node)


def radial_gradient(surface, node):
    """Store a radial gradient definition."""
    parse_def(surface, node)


def pattern(surface, node):
    """Store a pattern definition."""
    parse_def(surface, node)


def clip_path(surface, node):
    """Store a clip path definition."""
    surface.paths[node["id"]] = node


def paint_mask(surface, node, name, opacity):
    """Paint the mask of the current surface."""
    mask_node = surface.masks[name]
    mask_node.tag = "g"
    mask_node["opacity"] = opacity

    if mask_node.get("maskUnits") == "userSpaceOnUse":
        width_ref, height_ref = "x", "y"
    else:
        x = float(size(surface, node.get("x"), "x"))
        y = float(size(surface, node.get("y"), "y"))
        width = float(size(surface, node.get("width"), "x"))
        height = float(size(surface, node.get("height"), "y"))
        width_ref = width
        height_ref = height
        mask_node["transform"] = "%s scale(%f, %f)" % (
            mask_node.get("transform", ""), width, height)

    mask_node["x"] = float(
        size(surface, mask_node.get("x", "-10%"), width_ref))
    mask_node["y"] = float(
        size(surface, mask_node.get("y", "-10%"), height_ref))
    mask_node["height"] = float(
        size(surface, mask_node.get("height", "120%"), width_ref))
    mask_node["width"] = float(
        size(surface, mask_node.get("width", "120%"), height_ref))

    if mask_node.get("maskUnits") == "userSpaceOnUse":
        x = mask_node["x"]
        y = mask_node["y"]
        mask_node["viewBox"] = "%f %f %f %f" % (
            mask_node["x"], mask_node["y"],
            mask_node["width"], mask_node["height"])

    from . import SVGSurface  # circular import
    mask_surface = SVGSurface(mask_node, None, surface.dpi, surface)
    surface.context.save()
    surface.context.translate(x, y)
    surface.context.mask_surface(mask_surface.cairo)
    surface.context.restore()


def draw_gradient(surface, node, name):
    """Gradients colors."""
    gradient_node = surface.gradients[name]

    transform(surface, gradient_node.get("gradientTransform"))

    if gradient_node.get("gradientUnits") == "userSpaceOnUse":
        width_ref, height_ref = "x", "y"
        diagonal_ref = "xy"
    else:
        x = float(size(surface, node.get("x"), "x"))
        y = float(size(surface, node.get("y"), "y"))
        width = float(size(surface, node.get("width"), "x"))
        height = float(size(surface, node.get("height"), "y"))
        width_ref = height_ref = diagonal_ref = 1

    if gradient_node.tag == "linearGradient":
        x1 = float(size(surface, gradient_node.get("x1", "0%"), width_ref))
        x2 = float(size(surface, gradient_node.get("x2", "100%"), width_ref))
        y1 = float(size(surface, gradient_node.get("y1", "0%"), height_ref))
        y2 = float(size(surface, gradient_node.get("y2", "0%"), height_ref))
        gradient_pattern = cairo.LinearGradient(x1, y1, x2, y2)

    elif gradient_node.tag == "radialGradient":
        r = float(size(surface, gradient_node.get("r", "50%"), diagonal_ref))
        cx = float(size(surface, gradient_node.get("cx", "50%"), width_ref))
        cy = float(size(surface, gradient_node.get("cy", "50%"), height_ref))
        fx = float(size(surface, gradient_node.get("fx", str(cx)), width_ref))
        fy = float(size(surface, gradient_node.get("fy", str(cy)), height_ref))
        gradient_pattern = cairo.RadialGradient(fx, fy, 0, cx, cy, r)

    if gradient_node.get("gradientUnits") != "userSpaceOnUse":
        gradient_pattern.set_matrix(cairo.Matrix(
            1 / width, 0, 0, 1 / height, - x / width, - y / height))
    gradient_pattern.set_extend(getattr(
        cairo, "EXTEND_%s" % node.get("spreadMethod", "pad").upper()))

    offset = 0
    for child in gradient_node.children:
        offset = max(offset, size(surface, child.get("offset"), 1))
        stop_color = color(
            child.get("stop-color", "black"),
            float(child.get("stop-opacity", 1)))
        gradient_pattern.add_color_stop_rgba(offset, *stop_color)

    gradient_pattern.set_extend(getattr(
        cairo, "EXTEND_%s" % gradient_node.get("spreadMethod", "pad").upper()))

    surface.context.set_source(gradient_pattern)
    return True


def draw_pattern(surface, node, name):
    """Draw a pattern image."""
    pattern_node = surface.patterns[name]
    pattern_node.tag = "g"
    transform(surface, "translate(%s %s)" % (
        pattern_node.get("x"), pattern_node.get("y")))
    transform(surface, pattern_node.get("patternTransform"))

    if not pattern_node.get("viewBox") and not (
            size(surface, pattern_node.get("width", 0), 1) and
            size(surface, pattern_node.get("height", 0), 1)):
        return False

    if pattern_node.get("patternUnits") == "userSpaceOnUse":
        pattern_width =  \
            float(size(surface, pattern_node.get("width", 0), 1))
        pattern_height =  \
            float(size(surface, pattern_node.get("height", 0), 1))
    else:
        width = float(size(surface, node.get("width"), "x"))
        height = float(size(surface, node.get("height"), "y"))
        pattern_width = \
            size(surface, pattern_node.pop("width", "0"), 1) * width
        pattern_height = \
            size(surface, pattern_node.pop("height", "0"), 1) * height
        if "viewBox" not in pattern_node:
            pattern_node["width"] = pattern_width
            pattern_node["height"] = pattern_height
    from . import SVGSurface  # circular import
    pattern_surface = SVGSurface(pattern_node, None, surface.dpi, surface)
    pattern_pattern = cairo.SurfacePattern(pattern_surface.cairo)
    pattern_pattern.set_extend(cairo.EXTEND_REPEAT)
    pattern_pattern.set_matrix(cairo.Matrix(
        pattern_surface.width / pattern_width, 0, 0,
        pattern_surface.height / pattern_height, 0, 0))
    surface.context.set_source(pattern_pattern)
    return True


def draw_marker(surface, node, position="mid"):
    """Draw a marker."""
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

        if angle1 is None:
            angle1 = angle2

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

                width, height, viewbox = node_format(surface, marker_node)
                if viewbox:
                    viewbox_width = viewbox[2] - viewbox[0]
                    viewbox_height = viewbox[3] - viewbox[1]
                else:
                    viewbox_width = width or 0
                    viewbox_height = height or 0

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
    if "mask" in node:
        del node["mask"]
    href = node.get("{http://www.w3.org/1999/xlink}href")
    tree_urls = urls(href)
    url = tree_urls[0] if tree_urls else None
    tree = Tree(url=url, parent=node)
    surface.set_context_size(*node_format(surface, tree))
    surface.draw(tree)
    surface.context.restore()
    # Restore twice, because draw does not restore at the end of svg tags
    if tree.tag != "use":
        surface.context.restore()

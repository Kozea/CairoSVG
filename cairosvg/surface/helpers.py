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
Surface helpers.

"""

from math import pi, cos, sin, atan

from .units import size


def distance(x1, y1, x2, y2):
    """Get the distance between two points."""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def filter_fill_content(node):
    """Extract the content of fill and remove unnecessary characters."""
    content = list(urls(node.get("fill")))[0]
    if "url" in node.get("fill"):
        if not content.startswith("#"):
            return
        content = content[1:]
    return content


def node_format(node):
    """Return ``(width, height, viewbox)`` of ``node``."""
    width = size(node.get("width"))
    height = size(node.get("height"))
    viewbox = node.get("viewBox")
    if viewbox:
        viewbox = tuple(size(pos) for pos in viewbox.split())
        width = width or viewbox[2]
        height = height or viewbox[3]
    return width, height, viewbox


def normalize(string=None):
    """Normalize a string corresponding to an array of various vaues."""
    string = string.replace("-", " -")
    string = string.replace(",", " ")

    while "  " in string:
        string = string.replace("  ", " ")

    return string


def point(string=None):
    """Return ``(x, y, trailing_text)`` from ``string``."""
    if not string:
        return (0, 0, "")

    x, y, string = (string.strip() + " ").split(" ", 2)
    return size(x), size(y), string


def point_angle(cx, cy, px, py):
    """Return angle between x axis and point knowing given center."""
    angle = pi if cx > px else 0
    angle *= -1 if cy > py else 1
    angle += atan((cy - py) * (1 / (cx - px)) if (cx - px) else float("inf"))
    return angle


def preserve_ratio(surface, node):
    """Manage the ratio preservation."""
    if node.tag == "marker":
        scale_x = size(node.get("markerWidth", "3"))
        scale_y = size(node.get("markerHeight", "3"))
        translate_x = -size(node.get("refX"))
        translate_y = -size(node.get("refY"))
    elif node.tag == "svg":
        width, height, viewbox = node_format(node)
        viewbox_width = viewbox[2] - viewbox[0]
        viewbox_height = viewbox[3] - viewbox[1]
        scale_x = width / viewbox_width
        scale_y = height / viewbox_height

        align = node.get("preserveAspectRatio", "xMidYMid").split(" ")[0]
        if align != "none":
            mos_properties = node.get("preserveAspectRatio", "").split(' ')
            if mos_properties:
                meet_or_slice = mos_properties[1]
            if meet_or_slice == "slice":
                scale_value = max(scale_x, scale_y)
            else:
                scale_value = min(scale_x, scale_y)
            scale_x = scale_y = scale_value

            x_position = align[1:4].lower()
            y_position = align[5:].lower()

            if x_position == "min":
                translate_x = 0

            if y_position == "min":
                translate_y = 0

            if x_position == "mid":
                translate_x = (width / scale_x - viewbox_width) / 2.

            if y_position == "mid":
                translate_y = (height / scale_y - viewbox_height) / 2.

            if x_position == "max":
                translate_x = width / scale_x - viewbox_width

            if y_position == "max":
                translate_y = height / scale_y - viewbox_height

            surface.context.rectangle(0, 0, width, height)
            surface.context.clip()
        else:
            return

    return scale_x, scale_y, translate_x, translate_y


def quadratic_points(x1, y1, x2, y2, x3, y3):
    """Return the quadratic points to create quadratic curves."""
    xq1 = x2 * 2 / 3 + x1 / 3
    yq1 = y2 * 2 / 3 + y1 / 3
    xq2 = x2 * 2 / 3 + x3 / 3
    yq2 = y2 * 2 / 3 + y3 / 3
    return xq1, yq1, xq2, yq2, x3, y3


def rotate(x, y, angle):
    """Rotate a point of an angle around the origin point."""
    return x * cos(angle) - y * sin(angle), y * cos(angle) + x * sin(angle)


def urls(string):
    """Parse a comma-separated list of url() strings."""
    for link in string.split(","):
        link = link.strip()
        if link.startswith("url"):
            link = link[3:]
        yield link.strip("() ")

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
Shapes drawers.

"""

from math import pi

from .helpers import normalize, point, size


def circle(surface, node):
    """Draw a circle ``node`` on ``surface``."""
    surface.context.new_sub_path()
    surface.context.arc(
        size(node.get("x")) + size(node.get("cx")),
        size(node.get("y")) + size(node.get("cy")),
        size(node.get("r")), 0, 2 * pi)


def ellipse(surface, node):
    """Draw an ellipse ``node`` on ``surface``."""
    y_scale_ratio = size(node.get("ry")) / size(node.get("rx"))
    surface.context.new_sub_path()
    surface.context.save()
    surface.context.scale(1, y_scale_ratio)
    surface.context.arc(
        size(node.get("x")) + size(node.get("cx")),
        (size(node.get("y")) + size(node.get("cy"))) / y_scale_ratio,
        size(node.get("rx")), 0, 2 * pi)
    surface.context.restore()


def line(surface, node):
    """Draw a line ``node``."""
    x1, y1, x2, y2 = tuple(
        size(node.get(position)) for position in ("x1", "y1", "x2", "y2"))
    surface.context.move_to(x1, y1)
    surface.context.line_to(x2, y2)


def polygon(surface, node):
    """Draw a polygon ``node`` on ``surface``."""
    polyline(surface, node)
    surface.context.close_path()


def polyline(surface, node):
    """Draw a polyline ``node``."""
    points = normalize(node.get("points"))
    if points:
        x, y, points = point(points)
        surface.context.move_to(x, y)
        while points:
            x, y, points = point(points)
            surface.context.line_to(x, y)


def rect(surface, node):
    """Draw a rect ``node`` on ``surface``."""
    x, y = size(node.get("x")), size(node.get("y"))
    width, height = size(node.get("width")), size(node.get("height"))
    if size(node.get("rx")) == 0:
        surface.context.rectangle(x, y, width, height)
    else:
        r = size(node.get("rx"))
        a, b, c, d = x, width + x, y, height + y
        if r > width - r:
            r = width / 2
        surface.context.move_to(x, y + height / 2)
        surface.context.arc(a + r, c + r, r, 2 * pi / 2, 3 * pi / 2)
        surface.context.arc(b - r, c + r, r, 3 * pi / 2, 0 * pi / 2)
        surface.context.arc(b - r, d - r, r, 0 * pi / 2, 1 * pi / 2)
        surface.context.arc(a + r, d - r, r, 1 * pi / 2, 2 * pi / 2)
        surface.context.close_path()

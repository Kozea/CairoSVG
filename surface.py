# -*- coding: utf-8 -*-
# This file is part of CairoSVG
# Copyright © 2010 Kozea
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
Cairo surface creator

"""

import cairo
from math import pi

# TODO: find a real way to determine DPI
DPI = 72.
UNITS = {
    "mm": DPI / 25.4,
    "cm": DPI / 2.54,
    "in": DPI,
    "pt": DPI / 72.,
    "pc": DPI / 6.,
    "px": 1.,
    "em": NotImplemented,
    "ex": NotImplemented,
    "%": NotImplemented}


def size(string=None):
    """Replace a string with units by a float value."""
    if not string:
        return 0

    if string.replace(".", "", 1).isdigit():
        return float(string)

    for unit, value in UNITS.items():
        if unit in string:
            return float(string.strip(" " + unit)) * value


def color(string=None):
    """Replace ``string`` representing a color by a RGBA tuple."""
    if not string:
        return (0, 0, 0, 0)

    if "#" in string:
        if len(string) == 7:
            string += "ff"
        return tuple(int(value, 16)/255. for value in (
            string[1:3], string[3:5], string[5:7], string[7:9]))

    # TODO: manage other color types
    raise NotImplemented


def point(string=None):
    """Return ``(x, y, trailing_text)`` from ``string``."""
    if not string:
        return (0, 0, "")

    x, string = string.split(",", 1)
    y, string = string.split(" ", 1)
    return size(x), size(y), string


class Surface(object):
    """Cairo PDF surface."""
    # Cairo developers say that there is no way to inherit from cairo.*Surface
    def __init__(self, tree):
        """Create the surface from ``tree``."""
        width = size(tree.get("width", 0))
        height = size(tree.get("height", 0))
        self.cairo = cairo.PDFSurface("test.pdf", width, height)
        self.context = cairo.Context(self.cairo)

        viewbox = tree.get("viewBox")
        if viewbox:
            x1, y1, x2, y2 = tuple(size(pos) for pos in viewbox.split())
            self.context.scale(width/(x2 - x1), height/(y2 - y1))
            self.context.translate(-x1, -y1)

        self.draw(tree)

    def draw(self, node):
        """Draw ``node`` and its children."""
        if node.get("transform"):
            self.context.save()
            transformations = node["transform"].split(")")
            for transformation in transformations:
                transformation = transformation.strip()
                for ttype in ("scale", "translate"):
                    if ttype in transformation:
                        transformation = transformation.replace(ttype, "")
                        transformation = transformation.replace("(", "")
                        x, y = tuple(size(position.strip()) for position
                                     in transformation.split(","))
                        getattr(self.context, ttype)(x, y)

        if hasattr(self, node.tag):
            getattr(self, node.tag)(node)

        self.context.set_line_width(size(node.get("stroke-width")))
        self.context.set_source_rgba(*color(node.get("stroke")))
        self.context.stroke_preserve()

        if node.get("fill-rule") == "evenodd":
            self.context.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        self.context.set_source_rgba(*color(node.get("fill")))
        self.context.fill()

        for child in node.children:
            self.draw(child)

        if node.get("transform"):
            self.context.restore()

    def circle(self, node):
        """Draw a circle ``node``."""
        self.context.arc(
            size(node.get("x")) + size(node.get("cx")),
            size(node.get("y")) + size(node.get("cy")),
            size(node.get("r")), 0, 2*pi)

    def path(self, node):
        """Draw a path ``node``."""
        # Add sentinel
        string = node.get("d", "").strip() + " X X"
            
        while string:
            letter, string = string.split(" ", 1)
            string = string.strip()
            if letter == "C":
                # Curve
                x1, y1, string = point(string)
                x2, y2, string = point(string)
                x3, y3, string = point(string)
                self.context.curve_to(x1, y1, x2, y2, x3, y3)
            elif letter == "M":
                # Current point move
                x, y, string = point(string)
                self.context.move_to(x, y)
            elif letter == "L":
                # Straight line
                x, y, string = point(string)
                self.context.line_to(x, y)
            elif letter == "X":
                # Sentinel: stop
                string = ""
            elif letter == "Z":
                # End of path
                self.context.close_path()
            else:
                # TODO: manage other letters
                raise NotImplemented
            string = string.strip()

    def line(self, node):
        """Draw a line ``node``."""
        x1, y1, x2, y2 = tuple(size(position) for position in (
                node.get("x1"), node.get("y1"), node.get("x2"), node.get("y2")))
        self.context.move_to(x1, y1)
        self.context.line_to(x2, y2)

    def text(self, node):
        """Draw a text ``node``."""
        # TODO: manage tspan nodes
        if not node.get("fill"):
            # Black is the default text color
            node["fill"] = "#000000"

        self.context.select_font_face(
            "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(size(node.get("font-size", "12pt")))

        x_bearing, y_bearing, width, height, x_advance, y_advance = \
            self.context.text_extents(node.text)
        x, y = size(node.get("x")), size(node.get("y"))
        text_anchor = node.get("text-anchor")
        if text_anchor == "middle":
            x -= width/2. + x_bearing
        elif text_anchor == "end":
            x -= width + x_bearing
        
        self.context.move_to(x, y)
        self.context.set_source_rgba(*color(node.get("fill")))
        self.context.show_text(node.text)
        self.context.move_to(x, y)
        self.context.text_path(node.text)
        node["fill"] = "#00000000"

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
Cairo surface creator.

"""

# Ignore small variable names here
# pylint: disable=C0103

import abc
import cairo
import io
import itertools
from math import pi, cos, sin, atan, radians

from .parser import Tree
from .colors import COLORS

DPI = 72.
UNITS = {
    "mm": 1 / 25.4,
    "cm": 1 / 2.54,
    "in": 1,
    "pt": 1 / 72.,
    "pc": 1 / 6.,
    "px": None,
    "em": NotImplemented,
    "ex": NotImplemented,
    "%": NotImplemented}
PATH_LETTERS = "achlmqstvzACHLMQSTVZ"
PATH_TAGS = ("circle", "line", "path", "polyline", "polygon", "rect")


def normalize(string=None):
    """Normalize a string corresponding to an array of various vaues."""
    string = string.replace("-", " -")
    string = string.replace(",", " ")

    while "  " in string:
        string = string.replace("  ", " ")

    return string


def size(string=None):
    """Replace a string with units by a float value."""
    if not string:
        return 0

    if string.replace(".", "", 1).lstrip(" -").isdigit():
        return float(string)

    for unit, coefficient in UNITS.items():
        if unit in string:
            number = float(string.strip(" " + unit))
            return number * (DPI * coefficient if coefficient else 1)

    # Unknown size or multiple sizes
    return 0


def filter_fill_content(node):
    """Extract the content of fill and remove unnecessary characters."""
    content = list(urls(node.get("fill")))[0]
    if "url" in node.get("fill"):
        if not content.startswith("#"):
            return
        content = content[1:]
    return content


def color(string=None, opacity=1):
    """Replace ``string`` representing a color by a RGBA tuple."""
    if not string or string == "none":
        return (0, 0, 0, 0)

    string = string.strip().lower()

    if string.startswith("rgba"):
        r, g, b, a = tuple(
            float(i) for i in string.strip(" rgba()").split(","))
        return r, g, b, a * opacity
    elif string.startswith("rgb"):
        r, g, b = tuple(float(i) for i in string.strip(" rgb()").split(","))
        return r, g, b, opacity

    if string in COLORS:
        string = COLORS[string]

    if len(string) in (4, 5):
        string = "#" + "".join(2 * char for char in string[1:])
    if len(string) == 9:
        opacity *= int(string[7:9], 16) / 255

    plain_color = tuple(
        int(value, 16) / 255. for value in (
            string[1:3], string[3:5], string[5:7]))
    return plain_color + (opacity,)


def urls(string):
    """Parse a comma-separated list of url() strings."""
    for link in string.split(","):
        link = link.strip()
        if link.startswith("url"):
            link = link[3:]
        yield link.strip("() ")


def point(string=None):
    """Return ``(x, y, trailing_text)`` from ``string``."""
    if not string:
        return (0, 0, "")

    x, y, string = (string.strip() + " ").split(" ", 2)
    return size(x), size(y), string


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


def quadratic_points(x1, y1, x2, y2, x3, y3):
    """Return the quadratic points to create quadratic curves."""
    xq1 = x2 * 2 / 3 + x1 / 3
    yq1 = y2 * 2 / 3 + y1 / 3
    xq2 = x2 * 2 / 3 + x3 / 3
    yq2 = y2 * 2 / 3 + y3 / 3
    return xq1, yq1, xq2, yq2, x3, y3


def point_angle(cx, cy, px, py):
    """Return angle between x axis and point knowing given center."""
    angle = pi if cx > px else 0
    angle *= -1 if cy > py else 1
    angle += atan((cy - py) * (1 / (cx - px)) if (cx - px) else float("inf"))
    return angle


def rotate(x, y, angle):
    """Rotate a point of an angle around the origin point."""
    return x * cos(angle) - y * sin(angle), y * cos(angle) + x * sin(angle)


def distance(x1, y1, x2, y2):
    """Get the distance between two points."""
    return ((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)) ** 0.5


def path_distance(path, width):
    """Get the point at ``width`` distance on ``path``."""
    total_length = 0
    for item in path:
        if item[0] == cairo.PATH_MOVE_TO:
            old_point = item[1]
        elif item[0] == cairo.PATH_LINE_TO:
            new_point = item[1]
            length = distance(
                old_point[0], old_point[1], new_point[0], new_point[1])
            total_length += length
            if total_length < width:
                old_point = new_point
            else:
                length -= total_length - width
                angle = point_angle(
                    old_point[0], old_point[1], new_point[0], new_point[1])
                x = cos(angle) * length + old_point[0]
                y = sin(angle) * length + old_point[1]
                return x, y


class Surface(object):
    """Cairo abstract surface."""
    # Cairo developers say that there is no way to inherit from cairo.*Surface
    __metaclass__ = abc.ABCMeta

    def __init__(self, tree):
        """Create the surface from ``tree``."""
        self.cairo = None
        self.context = None
        self.cursor_position = 0, 0
        self.width_tot = 0
        self.markers = {}
        self.gradients = {}
        self.patterns = {}
        self.paths = {}
        self._old_parent_node = self.parent_node = None
        self.bytesio = io.BytesIO()
        self._create_surface(tree)
        self.draw(tree)

    @abc.abstractmethod
    def _create_surface(self, tree):
        """Create a cairo surface.

        A method overriding this one must create ``self.cairo`` and
        ``self.context``.

        """
        raise NotImplementedError

    def _parse_defs(self, node):
        """Parse the SVG definitions."""
        # Draw children
        for child in node.children:
            if child.tag == "marker":
                self.markers[child["id"]] = child
            if "gradient" in child.tag.lower():
                self.gradients[child["id"]] = child
            if "pattern" in child.tag.lower():
                self.patterns[child["id"]] = child
            if "path" in child.tag:
                self.paths[child["id"]] = child

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
        # Ignore defs
        if node.tag == "defs":
            self._parse_defs(node)
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
                            self.context.rotate(radians(float(values[0])))
                        elif ttype == "skewX":
                            matrix = self.context.get_matrix()
                            degree = radians(float(values[0]))
                            mtrx = cairo.Matrix(
                                matrix[0], matrix[1], matrix[2] + degree,
                                matrix[3], matrix[4], matrix[5])
                            self.context.set_matrix(mtrx)
                        elif ttype == "skewY":
                            matrix = self.context.get_matrix()
                            degree = radians(float(values[0]))
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

        if hasattr(self, node.tag):
            getattr(self, node.tag)(node)

        # Get stroke and fill opacity
        opacity = float(node.get("opacity", 1))
        stroke_opacity = opacity * float(node.get("stroke-opacity", 1))
        fill_opacity = opacity * float(node.get("fill-opacity", 1))

        if stroke_and_fill:
            # Fill
            if "url(#" in node.get("fill", ""):
                self._gradient_or_pattern(node)
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
        for child in node.children:
            self.draw(child, stroke_and_fill)

        if not node.root:
            # Restoring context is useless if we are in the root tag, it may
            # raise an exception if we have multiple svg tags
            self.context.restore()

        self.parent_node = self._old_parent_node

    def circle(self, node):
        """Draw a circle ``node``."""
        self.context.new_sub_path()
        self.context.arc(
            size(node.get("x")) + size(node.get("cx")),
            size(node.get("y")) + size(node.get("cy")),
            size(node.get("r")), 0, 2 * pi)

    def ellipse(self, node):
        """Draw an ellipse ``node``."""
        y_scale_ratio = size(node.get("ry")) / size(node.get("rx"))
        self.context.new_sub_path()
        self.context.save()
        self.context.scale(1, y_scale_ratio)
        self.context.arc(
            size(node.get("x")) + size(node.get("cx")),
            (size(node.get("y")) + size(node.get("cy"))) / y_scale_ratio,
            size(node.get("rx")), 0, 2 * pi)
        self.context.restore()

    def _gradient_or_pattern(self, node):
        name = filter_fill_content(node)
        if name in self.gradients:
            return self._gradient(node)
        elif name in self.patterns:
            return self._pattern(node)

    def _gradient(self, node):
        """Gradients colors."""
        gradient = filter_fill_content(node)
        gradient_node = self.gradients[gradient]

        if "x" not in node or "y" not in node:
            return
        x = float(size(node.get("x")))
        y = float(size(node.get("y")))
        height = float(size(node.get("height")))
        width = float(size(node.get("width")))
        x1 = float(gradient_node.get("x1", x))
        x2 = float(gradient_node.get("x2", x + width))
        y1 = float(gradient_node.get("y1", y))
        y2 = float(gradient_node.get("y2", y + height))

        if gradient_node.tag == "linearGradient":
            linpat = cairo.LinearGradient(x1, y1, x2, y2)
            for child in gradient_node.children:
                offset = child.get("offset")
                stop_color = color(child.get("stop-color"))
                offset = child.get("offset")
                if "%" in offset:
                    offset = float(offset.strip("%")) / 100
                linpat.add_color_stop_rgba(float(offset), *stop_color)
            self.context.set_source(linpat)
            self.context.fill_preserve()
        elif gradient_node.tag == "radialGradient":
        # TODO: manage percentages for default values
            r = float(gradient_node.get("r"))
            cx = float(gradient_node.get("cx"))
            cy = float(gradient_node.get("cy"))
            fx = float(gradient_node.get("fx"))
            fy = float(gradient_node.get("fy"))
            radpat = cairo.RadialGradient(fx, fy, 0, cx, cy, r)

            for child in gradient_node.children:
                offset = child.get("offset")
                stop_color = color(child.get("stop-color"))
                radpat.add_color_stop_rgba(
                    float(offset.strip("%")) / 100, *stop_color)
            self.context.set_source(radpat)
            self.context.fill_preserve()

    def _marker(self, node, position="mid"):
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
            self.context.get_current_point(), node.markers[position])

        if position == "start":
            node.pending_markers.append(pending_marker)
            return
        elif position == "end":
            node.pending_markers.append(pending_marker)

        while node.pending_markers:
            next_point, markers = node.pending_markers.pop(0)

            if node.tangents != []:
                angle1 = node.tangents.pop(0)
            if node.tangents != []:
                angle2 = node.tangents.pop(0)

            for marker in markers:
                if not marker.startswith("#"):
                    continue
                marker = marker[1:]
                if marker in self.markers:
                    marker_node = self.markers[marker]

                    angle = marker_node.get("orient", "0")
                    if angle == "auto":
                        if angle1 is None:
                            angle1 = angle2
                        angle = float(angle1 + angle2) / 2
                    else:
                        angle = radians(float(angle))

                    temp_path = self.context.copy_path()
                    current_x, current_y = next_point

                    if node.get("markerUnits") == "userSpaceOnUse":
                        base_scale = 1
                    else:
                        base_scale = size(self.parent_node.get("stroke-width"))

                    # Returns 4 values
                    scale_x, scale_y, translate_x, translate_y = \
                        self._preserve_ratio(marker_node)

                    viewbox = node_format(marker_node)[-1]
                    viewbox_width = viewbox[2] - viewbox[0]
                    viewbox_height = viewbox[3] - viewbox[1]

                    self.context.new_path()
                    for child in marker_node.children:
                        self.context.save()
                        self.context.translate(current_x, current_y)
                        self.context.rotate(angle)
                        self.context.scale(
                            base_scale / viewbox_width * float(scale_x),
                            base_scale / viewbox_height * float(scale_y))
                        self.context.translate(translate_x, translate_y)
                        self.draw(child)
                        self.context.restore()
                    self.context.append_path(temp_path)

        if position == "mid":
            node.pending_markers.append(pending_marker)

    def _preserve_ratio(self, node):
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

                self.context.rectangle(0, 0, width, height)
                self.context.clip()
            else:
                return

        return scale_x, scale_y, translate_x, translate_y

    def _pattern(self, node):
        """Draw a pattern image."""
        pattern = filter_fill_content(node)
        pattern_node = self.patterns[pattern]
        if pattern_node.tag == "pattern":
            surface = DummySurface(pattern_node)
            pattern = cairo.SurfacePattern(surface.cairo)
            pattern.set_extend(cairo.EXTEND_REPEAT)
            self.context.set_source(pattern)
            self.context.fill_preserve()

    def path(self, node):
        """Draw a path ``node``."""
        string = node.get("d", "")
        self._marker(node, "start")

        for letter in PATH_LETTERS:
            string = string.replace(letter, " %s " % letter)

        last_letter = None
        string = normalize(string)

        while string:
            string = string.strip()
            if string.split(" ", 1)[0] in PATH_LETTERS:
                letter, string = (string + " ").split(" ", 1)

            if letter in "aA":
                # Elliptic curve
                x1, y1 = self.context.get_current_point()
                rx, ry, string = point(string)
                radii_ratio = ry / rx
                rotation, large, sweep, string = string.split(" ", 3)
                rotation = radians(float(rotation))
                large, sweep = bool(int(large)), bool(int(sweep))
                x3, y3, string = point(string)

                if letter == "A":
                    # Absolute x3 and y3, convert to relative
                    x3 -= x1
                    y3 -= y1

                # Cancel the rotation of the second point
                xe, ye = rotate(x3, y3, -rotation)
                ye /= radii_ratio

                # Find the angle between the second point and the x axis
                angle = point_angle(0, 0, xe, ye)

                # Put the second point onto the x axis
                xe = (xe ** 2 + ye ** 2) ** .5
                ye = 0

                # Update the x radius if it is too small
                rx = max(rx, xe / 2)

                # Find one circle centre
                xc = xe / 2
                yc = (rx ** 2 - xc ** 2) ** .5

                # Choose between the two circles according to flags
                if not (large ^ sweep):
                    yc = -yc

                # Define the arc sweep
                arc = self.context.arc if sweep else self.context.arc_negative

                # Put the second point and the center back to their positions
                xe, ye = rotate(xe, 0, angle)
                xc, yc = rotate(xc, yc, angle)

                # Find the drawing angles
                angle1 = point_angle(xc, yc, 0, 0)
                angle2 = point_angle(xc, yc, xe, ye)

                # Store the tangent angles
                node.tangents.extend((-angle1, -angle2))

                # Draw the arc
                self.context.save()
                self.context.translate(x1, y1)
                self.context.rotate(rotation)
                self.context.scale(1, radii_ratio)
                arc(xc, yc, rx, angle1, angle2)
                self.context.restore()

            elif letter == "c":
                # Relative curve
                x1, y1, string = point(string)
                x2, y2, string = point(string)
                x3, y3, string = point(string)
                node.tangents.extend((
                    point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
                self.context.rel_curve_to(x1, y1, x2, y2, x3, y3)

            elif letter == "C":
                # Curve
                x1, y1, string = point(string)
                x2, y2, string = point(string)
                x3, y3, string = point(string)
                node.tangents.extend((
                    point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
                self.context.curve_to(x1, y1, x2, y2, x3, y3)

            elif letter == "h":
                # Relative horizontal line
                x, string = string.split(" ", 1)
                angle = 0 if x > 0 else pi
                node.tangents.extend((-angle, angle))
                self.context.rel_line_to(size(x), 0)

            elif letter == "H":
                # Horizontal line
                x, string = string.split(" ", 1)
                old_x = self.context.get_current_point()[1]
                angle = 0 if x > old_x else pi
                node.tangents.extend((-angle, angle))
                self.context.line_to(size(x), old_x)

            elif letter == "l":
                # Relative straight line
                x, y, string = point(string)
                angle = point_angle(0, 0, x, y)
                node.tangents.extend((-angle, angle))
                self.context.rel_line_to(x, y)

            elif letter == "L":
                # Straight line
                x, y, string = point(string)
                old_x, old_y = self.context.get_current_point()
                angle = point_angle(old_x, old_y, x, y)
                node.tangents.extend((-angle, angle))
                self.context.line_to(x, y)

            elif letter == "m":
                # Current point relative move
                x, y, string = point(string)
                self.context.rel_move_to(x, y)

            elif letter == "M":
                # Current point move
                x, y, string = point(string)
                self.context.move_to(x, y)

            elif letter == "q":
                # Relative quadratic curve
                # TODO: manage next letter "T"
                # TODO: manage tangents
                string, next_string = string.split("t", 1)
                x1, y1 = 0, 0
                while string:
                    x2, y2, string = point(string)
                    x3, y3, string = point(string)
                    xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                        x1, y1, x2, y2, x3, y3)
                    self.context.rel_curve_to(xq1, yq1, xq2, yq2, xq3, yq3)
                node.tangents.extend((0, 0))
                string = "t" + next_string

            elif letter == "Q":
                # Quadratic curve
                # TODO: manage next letter "t"
                # TODO: manage tangents
                string, next_string = string.split("T", 1)
                x1, y1 = self.context.get_current_point()
                while string:
                    x2, y2, string = point(string)
                    x3, y3, string = point(string)
                    xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                        x1, y1, x2, y2, x3, y3)
                    self.context.curve_to(xq1, yq1, xq2, yq2, xq3, yq3)
                node.tangents.extend((0, 0))
                string = "T" + next_string

            elif letter == "s":
                # Relative smooth curve
                # TODO: manage last_letter in "CS"
                # TODO: manage tangents
                x1 = x3 - x2 if last_letter in "cs" else 0
                y1 = y3 - y2 if last_letter in "cs" else 0
                x2, y2, string = point(string)
                x3, y3, string = point(string)
                node.tangents.extend((
                    point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
                self.context.rel_curve_to(x1, y1, x2, y2, x3, y3)

            elif letter == "S":
                # Smooth curve
                # TODO: manage last_letter in "cs"
                # TODO: manage tangents
                x, y = self.context.get_current_point()
                x2, y2, string = point(string)
                x1 = x3 if last_letter in "CS" else x
                y1 = y2 if last_letter in "CS" else y
                x3, y3, string = point(string)
                node.tangents.extend((
                    point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
                self.context.curve_to(x1, y1, x2, y2, x3, y3)

            elif letter == "t":
                # Relative quadratic curve end
                # TODO: manage tangents
                x1, y1 = 0, 0
                x2 = 2 * x1 - x2
                y2 = 2 * y1 - y2
                x3, y3, string = point(string)
                xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                    x1, y1, x2, y2, x3, y3)
                node.tangents.extend((0, 0))
                self.context.rel_curve_to(xq1, yq1, xq2, yq2, xq3, yq3)

            elif letter == "T":
                # Quadratic curve end
                # TODO: manage tangents
                x1, y1 = self.context.get_current_point()
                x2 = 2 * x1 - x2
                y2 = 2 * y1 - y2
                x3, y3, string = point(string)
                xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                    x1, y1, x2, y2, x3, y3)
                node.tangents.extend((0, 0))
                self.context.curve_to(xq1, yq1, xq2, yq2, xq3, yq3)

            elif letter == "v":
                # Relative vertical line
                y, string = string.split(" ", 1)
                angle = pi / 2 if y > 0 else -pi / 2
                node.tangents.extend((-angle, angle))
                self.context.rel_line_to(0, size(y))

            elif letter == "V":
                # Vertical line
                y, string = string.split(" ", 1)
                old_y = self.context.get_current_point()[0]
                angle = pi / 2 if y > 0 else -pi / 2
                node.tangents.extend((-angle, angle))
                self.context.line_to(old_y, size(y))

            elif letter in "zZ":
                # End of path
                # TODO: manage tangents
                node.tangents.extend((0, 0))
                self.context.close_path()

            else:
                # TODO: manage other letters
                raise NotImplementedError

            string = string.strip()

            if string and letter not in "mM":
                self._marker(node, "mid")

            last_letter = letter

        node.tangents.append(node.tangents[-1])
        self._marker(node, "end")

    def line(self, node):
        """Draw a line ``node``."""
        x1, y1, x2, y2 = tuple(
            size(node.get(position)) for position in ("x1", "y1", "x2", "y2"))
        self.context.move_to(x1, y1)
        self.context.line_to(x2, y2)

    def polyline(self, node):
        """Draw a polyline ``node``."""
        points = normalize(node.get("points"))
        if points:
            x, y, points = point(points)
            self.context.move_to(x, y)
            while points:
                x, y, points = point(points)
                self.context.line_to(x, y)

    def polygon(self, node):
        """Draw a polygon ``node``."""
        self.polyline(node)
        self.context.close_path()

    def rect(self, node):
        """Draw a rect ``node``."""
        x, y = size(node.get("x")), size(node.get("y"))
        width, height = size(node.get("width")), size(node.get("height"))
        if size(node.get("rx")) == 0:
            self.context.rectangle(x, y, width, height)
        else:
            r = size(node.get("rx"))
            a, b, c, d = x, width + x, y, height + y
            if r > width - r:
                r = width / 2
            self.context.move_to(x, y + height / 2)
            self.context.arc(a + r, c + r, r, 2 * pi / 2, 3 * pi / 2)
            self.context.arc(b - r, c + r, r, 3 * pi / 2, 0 * pi / 2)
            self.context.arc(b - r, d - r, r, 0 * pi / 2, 1 * pi / 2)
            self.context.arc(a + r, d - r, r, 1 * pi / 2, 2 * pi / 2)
            self.context.close_path()

    def svg(self, node):
        """Draw a svg ``node``."""
        if node.get("preserveAspectRatio"):
            if node.get("preserveAspectRatio") != "none":
                scale_x, scale_y, translate_x, translate_y = \
                    self._preserve_ratio(node)
                self.context.translate(*self.context.get_current_point())
                self.context.scale(scale_x, scale_y)
                self.context.translate(translate_x, translate_y)
        else:
            return

    def tref(self, node):
        """Draw a tref ``node``."""
        self.use(node)

    def tspan(self, node):
        """Draw a tspan ``node``."""
        x, y = [[i] for i in self.cursor_position]
        if "x" in node:
            x = [size(i) for i in normalize(node["x"]).strip().split(" ")]
        if "y" in node:
            y = [size(i) for i in normalize(node["y"]).strip().split(" ")]

        text = node.text.strip()
        if not text:
            return
        fill = node.get("fill")
        positions = list(itertools.izip_longest(x, y))
        letters_positions = zip(positions, text)
        letters_positions = letters_positions[:-1] + [
            (letters_positions[-1][0], text[len(letters_positions) - 1:])]

        for (x, y), letters in letters_positions:
            if x == None:
                x = self.cursor_position[0]
            if y == None:
                y = self.cursor_position[1]
            node["x"] = str(x + size(node.get("dx")))
            node["y"] = str(y + size(node.get("dy")))
            node["fill"] = fill
            node.text = letters
            if node.parent.tag == "text":
                self.text(node)
            else:
                node["x"] = str(x + size(node.get("dx")))
                node["y"] = str(y + size(node.get("dy")))
                self.textPath(node)
                if node.parent.children[-1] == node:
                    self.width_tot = 0

    def text(self, node):
        """Draw a text ``node``."""
        # Set black as default text color
        if not node.get("fill"):
            node["fill"] = node.get("color") or "#000000"

        # TODO: find a better way to manage white spaces in text nodes
        node.text = (node.text or "").lstrip()
        node.text = node.text.rstrip() + " "

        # TODO: manage font variant
        font_size = size(node.get("font-size", "12pt"))
        font_family = node.get("font-family", "Sans")
        font_style = getattr(
            cairo, ("font_slant_%s" % node.get("font-style")).upper(),
            cairo.FONT_SLANT_NORMAL)
        font_weight = getattr(
            cairo, ("font_weight_%s" % node.get("font-weight")).upper(),
            cairo.FONT_WEIGHT_NORMAL)
        self.context.select_font_face(font_family, font_style, font_weight)
        self.context.set_font_size(font_size)

        text_extents = self.context.text_extents(node.text)
        x_bearing = text_extents[0]
        width = text_extents[2]
        x, y = size(node.get("x")), size(node.get("y"))
        text_anchor = node.get("text-anchor")
        style = node.get("style")
        if (text_anchor == "middle") or (style == "text-anchor:middle"):
            x -= width / 2. + x_bearing
        elif text_anchor == "end":
            x -= width + x_bearing

        # Get global text opacity
        opacity = float(node.get("opacity", 1))

        self.context.move_to(x, y)
        if "url(#" in node.get("fill"):
            self._gradient_or_pattern(node)
        else:
            self.context.set_source_rgba(*color(node.get("fill"), opacity))
        self.context.show_text(node.text)
        node["fill"] = "#00000000"

        # Remember the absolute cursor position
        self.cursor_position = self.context.get_current_point()

    def textPath(self, node):
        """Draw text on a path."""
        self.context.save()
        opacity = float(node.get("opacity", 1))
        if "url(#" not in node.get("fill"):
            self.context.set_source_rgba(*color(node.get("fill"), opacity))

        id_path = node.get("{http://www.w3.org/1999/xlink}href")
        if not id_path.startswith("#"):
            return
        id_path = id_path[1:]

        if id_path in self.paths:
            path = self.paths.get(id_path)
        else:
            return

        self.draw(path, False)
        cairo_path = self.context.copy_path_flat()
        self.context.new_path()

        x, y = path_distance(cairo_path, self.width_tot)
        text = node.text.strip(" \n")

        for letter in text:
            x_advance = self.context.text_extents(letter)[4]
            self.width_tot += x_advance
            x2, y2 = path_distance(cairo_path, self.width_tot)
            angle = point_angle(x, y, x2, y2)
            self.context.save()
            self.context.translate(x, y)
            self.context.rotate(angle)
            self.context.translate(0, size(node.get("y")))
            self.context.show_text(letter)
            self.context.restore()
            x, y = x2, y2
        self.context.restore()

        # Remember the relative cursor position
        self.cursor_position = size(node.get("x")), size(node.get("y"))

    def use(self, node):
        """Draw the content of another SVG file."""
        self.context.save()
        self.context.translate(size(node.get("x")), size(node.get("y")))
        if "x" in node:
            del node["x"]
        if "y" in node:
            del node["y"]
        if "viewBox" in node:
            del node["viewBox"]
        href = node.get("{http://www.w3.org/1999/xlink}href")
        tree = Tree(href, node)
        self._set_context_size(*node_format(tree))
        self.draw(tree)
        self.context.restore()
        # Restore twice, because draw does not restore at the end of svg tags
        self.context.restore()


class DummySurface(Surface):
    """ Dummy surface used as source for the pattern's images."""
    def _create_surface(self, tree):
        width, height, viewbox = node_format(tree)
        self.cairo = cairo.SVGSurface(None, width, height)
        self.context = cairo.Context(self.cairo)
        self._set_context_size(width, height, viewbox)
        self.context.move_to(0, 0)


# pylint: enable=C0103
